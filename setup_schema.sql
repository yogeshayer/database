-------------------------------------------------------------------
-- MAIN CONCERNS
-- Addressing: should we separate by Street,City, State, Zip
--				for each occurrence?
-- NULL Allowance: do values that are currently allowed to be NULL
-- 					have any negative potential?
-- Should a table be added for plant_make_vehicle? 
-- 		as in, should plants be responsible for tracking
--		manufacturing history, or should a vehicle itself
-- 		describe what plant it came from with plant_id? 
-------------------------------------------------------------------




-- all Brand NOT NULL -- primary ref brand_name
-- brand also known as 'make'
CREATE TABLE brand (
	brand_id SERIAL PRIMARY KEY,
	brand_name VARCHAR(50) NOT NULL UNIQUE,
	country VARCHAR(50) NOT NULL
);

-- models have different attributes that
-- may require diferent parts. 
-- REFS make/brand
--  are unique by make, model, and bodystyle
-- unique combination of brand, model, body
CREATE TABLE model (
	model_id SERIAL PRIMARY KEY,
	brand_id INT NOT NULL REFERENCES brand(brand_id),
	model_name VARCHAR(50) NOT NULL,
	body_style VARCHAR(50) NOT NULL,
	UNIQUE(brand_id, model_name, body_style)
);

-- model_gen provides metadata for the model
-- some models will have different years
-- but be the same gen
-- REFS model
-- start year should be known, but maybe not end year
CREATE TABLE model_generation(
	generation_id SERIAL PRIMARY KEY,
	model_id INT NOT NULL REFERENCES model(model_id),
	generation_name VARCHAR(50),
	year_start INT NOT NULL,
	year_end INT
);

-- Supplier -- (For Parts)
CREATE TABLE supplier (
	supplier_id SERIAL PRIMARY KEY,
	supplier_name VARCHAR(150) NOT NULL UNIQUE,
	contact_email VARCHAR(200),
	phone VARCHAR(20),
	country VARCHAR(100)
);
-- Part -- Distributed by supplier -- mult models
-- supplier_id NULL means unknown (salvaged? used?)
-- part_name -- spark plug, piston, brake pad, battery (always known)
-- part_type -- OEM, OES, aftermarket, etc. Can be listed Unknown
CREATE TABLE part (
	part_id SERIAL PRIMARY KEY,
	supplier_id INT REFERENCES supplier(supplier_id),
	part_number VARCHAR(100) NOT NULL,
	part_name VARCHAR(200) NOT NULL,
	part_category VARCHAR(50) NOT NULL,
	supply_start_date DATE,
	supply_end_date DATE,
	unit_cost DECIMAL(10,2)
);

-- Part works with this model_id 
-- somewhat inflated, but must be specific
-- in cases of model year and body style
-- (example: bumper for one model will change per
-- the year and )
--! Perhpas change model_id to generation_id???
--! In some cases, a generation might have diff parts?  I think
CREATE TABLE part_models (
	part_id INT NOT NULL REFERENCES part(part_id),
	model_id INT NOT NULL REFERENCES model(model_id),
	PRIMARY KEY (part_id, model_id)

); 


----------------------------------------------------------------------
-- 
----------------------------------------------------------------------

-- PLANT produces/manufactures vehicles to be distributed
--  a plant could potentially manufacture different models, makes, etc
-- produced_table necessary? as in, what vins came from a specific 
-- plant?
CREATE TABLE plant (
	plant_id SERIAL PRIMARY KEY,
	plant_name VARCHAR(150) NOT NULL,
	city VARCHAR(100),
	plant_state VARCHAR(50),
	country VARCHAR(100)
);
----------------------------------------------------------------------
-- VEHICLE refs a model_id, generation inferred through date?
--  ADD a check for CHECK status IN ('manufactured', 'inventory', etc)
--  is 
CREATE TABLE vehicle (
	vin VARCHAR(17) PRIMARY KEY,
	model_id INT NOT NULL REFERENCES model(model_id),
	plant_id INT REFERENCES plant(plant_id),
	model_year INT NOT NULL,
	color VARCHAR(50),
	mileage INT DEFAULT 0,
	CHECK (
		LENGTH(vin) = 17
		AND vin ~ '^[A-HJ-NPR-Z0-9]{17}$'
	)
);
----------------------------------------------------------------------


-- OPTION -- metadata for a specific vehicle?
CREATE TABLE vehicle_option(
	option_id SERIAL PRIMARY KEY,
	vin VARCHAR(17) NOT NULL REFERENCES vehicle(vin),
	option_name VARCHAR(150) NOT NULL,
	option_category VARCHAR(50),
	option_price DECIMAL(10,2) DEFAULT 0.00
);
-- DEALER
CREATE TABLE dealer (
	dealer_id SERIAL PRIMARY KEY,
	dealer_name VARCHAR(200) NOT NULL,
	address VARCHAR(300),
	city VARCHAR(100),
	dealer_state VARCHAR(50),
	zip VARCHAR(10),
	phone VARCHAR(20),
	email VARCHAR(200)
);

CREATE TABLE dealer_brand (
	dealer_id INT NOT NULL REFERENCES dealer(dealer_id),
	brand_id INT NOT NULL REFERENCES brand(brand_id),
	authorized_date DATE,
	PRIMARY KEY (dealer_id, brand_id)
);

--CUSTOMER
-- Gender: M, F, O -- Male, female, other
--  is income, address, necessary?
CREATE TABLE customer (
	customer_id SERIAL PRIMARY KEY,
	first_name VARCHAR(100) NOT NULL,
	last_name VARCHAR(100) NOT NULL,
	email VARCHAR(200) UNIQUE,
	phone VARCHAR(20),
	address VARCHAR(300),
	gender CHAR(1),
	income DECIMAL(12,2)
);

-- INVENTORY
-- undecided price may be null?
-- date sold may be NULL --> unsold
-- inventory is specifically a DEALERs inventory?
-- price is a working price, not fixed (allows sales price)
CREATE TABLE inventory(
	inventory_id SERIAL PRIMARY KEY,
	vin VARCHAR(17) NOT NULL REFERENCES vehicle(vin),
	dealer_id INT NOT NULL REFERENCES dealer(dealer_id),
	date_received DATE NOT NULL,
	date_sold DATE,
	sticker_price DECIMAL(12,2)
);


-- SALE --
--! Uses inventory id instead of vin & dealer
--! since inventory id identifies both
CREATE TABLE sale(
	sale_id SERIAL PRIMARY KEY,
	inventory_id INT NOT NULL REFERENCES inventory(inventory_id),
	customer_id INT NOT NULL REFERENCES customer(customer_id),
	sale_date DATE NOT NULL,
	sale_price DECIMAL(12,2) NOT NULL,
	salesperson VARCHAR(200),
	payment_method VARCHAR(50)
);

ALTER TABLE customer
ADD CONSTRAINT chk_customer_gender
CHECK (gender IN ('M', 'F', 'N', 'O') OR gender IS NULL);

ALTER TABLE inventory
ADD CONSTRAINT chk_inventory_dates
CHECK (date_sold IS NULL OR date_sold >= date_received);

ALTER TABLE model_generation
ADD CONSTRAINT chk_generation_years
CHECK (year_end IS NULL OR year_end >= year_start);


