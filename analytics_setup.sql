-- Adds missing customer link needed for gender/income sales reports
ALTER TABLE sale
ADD COLUMN IF NOT EXISTS customer_id INT REFERENCES customer(customer_id);

-- Adds realistic dealers
INSERT INTO dealer (dealer_name, address, city, dealer_state, phone)
VALUES
('Lone Star Auto Group', '2501 University Dr', 'Denton', 'TX', '940-555-1201'),
('DFW Premier Motors', '4100 Belt Line Rd', 'Addison', 'TX', '972-555-2388'),
('Dallas Luxury Auto', '6200 Lemmon Ave', 'Dallas', 'TX', '214-555-7821')
ON CONFLICT DO NOTHING;

-- Adds realistic customers
INSERT INTO customer (first_name, last_name, gender, income, phone, address)
VALUES
('John', 'Miller', 'M', 55000, '817-555-1111', '12 Oak St, Denton, TX'),
('Sarah', 'Johnson', 'F', 72000, '972-555-2222', '45 Pine St, Plano, TX'),
('Alex', 'Patel', 'M', 110000, '214-555-3333', '78 Maple Ave, Dallas, TX'),
('Emily', 'Garcia', 'F', 145000, '469-555-4444', '91 Cedar Dr, Frisco, TX'),
('Chris', 'Lee', 'O', 48000, '940-555-5555', '100 Fry St, Denton, TX')
ON CONFLICT DO NOTHING;

-- Adds brands
INSERT INTO brand (brand_name, country)
VALUES
('Toyota', 'Japan'),
('Ford', 'USA'),
('BMW', 'Germany'),
('Honda', 'Japan'),
('Mercedes-Benz', 'Germany'),
('Mazda', 'Japan')
ON CONFLICT (brand_name) DO NOTHING;

-- Adds models
INSERT INTO model (brand_id, model_name, body_style)
VALUES
((SELECT brand_id FROM brand WHERE brand_name = 'Toyota'), 'Camry', 'Sedan'),
((SELECT brand_id FROM brand WHERE brand_name = 'Toyota'), 'RAV4', 'SUV'),
((SELECT brand_id FROM brand WHERE brand_name = 'Ford'), 'Mustang', 'Convertible'),
((SELECT brand_id FROM brand WHERE brand_name = 'BMW'), '3 Series', 'Sedan'),
((SELECT brand_id FROM brand WHERE brand_name = 'Honda'), 'Civic', 'Sedan'),
((SELECT brand_id FROM brand WHERE brand_name = 'Mercedes-Benz'), 'C-Class Cabriolet', 'Convertible'),
((SELECT brand_id FROM brand WHERE brand_name = 'Mazda'), 'MX-5 Miata', 'Convertible')
ON CONFLICT (brand_id, model_name, body_style) DO NOTHING;

-- Adds plants
INSERT INTO plant (plant_name, city, plant_state)
VALUES
('Dallas Assembly', 'Dallas', 'TX'),
('Munich Plant', 'Munich', 'Bavaria'),
('Nagoya Plant', 'Nagoya', 'Aichi')
ON CONFLICT DO NOTHING;

-- Adds supplier Getrag
INSERT INTO supplier (supplier_name, address, contact_phone)
VALUES
('Getrag', '100 Transmission Way', '888-555-9000')
ON CONFLICT DO NOTHING;

-- Adds transmission part from Getrag
INSERT INTO part (supplier_id, part_name, part_type)
VALUES
((SELECT supplier_id FROM supplier WHERE supplier_name = 'Getrag'), 'Automatic Transmission', 'OEM')
ON CONFLICT DO NOTHING;

-- Connects Getrag transmission to selected models
INSERT INTO part_models (part_id, model_id)
SELECT
    (SELECT part_id FROM part WHERE part_name = 'Automatic Transmission' LIMIT 1),
    model_id
FROM model
WHERE model_name IN ('Mustang', '3 Series', 'C-Class Cabriolet')
ON CONFLICT DO NOTHING;

-- Adds vehicles
INSERT INTO vehicle (vin, model_id, manufacture_date, status, plant_id)
VALUES
('1HGCM82633A004352', (SELECT model_id FROM model WHERE model_name = 'Camry' LIMIT 1), '2024-01-15', 'sold', (SELECT plant_id FROM plant WHERE plant_name = 'Dallas Assembly' LIMIT 1)),
('2T1BURHE5JC123456', (SELECT model_id FROM model WHERE model_name = 'RAV4' LIMIT 1), '2024-02-20', 'sold', (SELECT plant_id FROM plant WHERE plant_name = 'Dallas Assembly' LIMIT 1)),
('1FAFP45X1XF123456', (SELECT model_id FROM model WHERE model_name = 'Mustang' LIMIT 1), '2024-03-10', 'sold', (SELECT plant_id FROM plant WHERE plant_name = 'Dallas Assembly' LIMIT 1)),
('WBA8D9G54JNU12345', (SELECT model_id FROM model WHERE model_name = '3 Series' LIMIT 1), '2024-04-05', 'sold', (SELECT plant_id FROM plant WHERE plant_name = 'Munich Plant' LIMIT 1)),
('19XFC2F59HE123456', (SELECT model_id FROM model WHERE model_name = 'Civic' LIMIT 1), '2023-06-12', 'sold', (SELECT plant_id FROM plant WHERE plant_name = 'Nagoya Plant' LIMIT 1)),
('WDDWK8DB1HF123456', (SELECT model_id FROM model WHERE model_name = 'C-Class Cabriolet' LIMIT 1), '2024-07-01', 'sold', (SELECT plant_id FROM plant WHERE plant_name = 'Munich Plant' LIMIT 1)),
('JM1NDAD70K0123456', (SELECT model_id FROM model WHERE model_name = 'MX-5 Miata' LIMIT 1), '2025-05-10', 'sold', (SELECT plant_id FROM plant WHERE plant_name = 'Nagoya Plant' LIMIT 1)),
('1FAFP45X1XF654321', (SELECT model_id FROM model WHERE model_name = 'Mustang' LIMIT 1), '2023-08-15', 'inventory', (SELECT plant_id FROM plant WHERE plant_name = 'Dallas Assembly' LIMIT 1))
ON CONFLICT (vin) DO NOTHING;

-- Adds inventory
INSERT INTO inventory (dealer_id, vin, date_received, date_sold, price)
VALUES
((SELECT dealer_id FROM dealer WHERE dealer_name = 'Lone Star Auto Group' LIMIT 1), '1HGCM82633A004352', '2024-01-20', '2024-03-10', 28000),
((SELECT dealer_id FROM dealer WHERE dealer_name = 'Lone Star Auto Group' LIMIT 1), '2T1BURHE5JC123456', '2024-02-25', '2024-05-15', 33000),
((SELECT dealer_id FROM dealer WHERE dealer_name = 'DFW Premier Motors' LIMIT 1), '1FAFP45X1XF123456', '2024-03-15', '2024-06-20', 46000),
((SELECT dealer_id FROM dealer WHERE dealer_name = 'Dallas Luxury Auto' LIMIT 1), 'WBA8D9G54JNU12345', '2024-04-10', '2024-08-01', 51000),
((SELECT dealer_id FROM dealer WHERE dealer_name = 'Lone Star Auto Group' LIMIT 1), '19XFC2F59HE123456', '2023-06-18', '2023-09-12', 26000),
((SELECT dealer_id FROM dealer WHERE dealer_name = 'Dallas Luxury Auto' LIMIT 1), 'WDDWK8DB1HF123456', '2024-07-05', '2024-07-30', 62000),
((SELECT dealer_id FROM dealer WHERE dealer_name = 'DFW Premier Motors' LIMIT 1), 'JM1NDAD70K0123456', '2025-05-15', '2025-06-12', 35000),
((SELECT dealer_id FROM dealer WHERE dealer_name = 'DFW Premier Motors' LIMIT 1), '1FAFP45X1XF654321', '2023-08-20', NULL, 42000)
ON CONFLICT DO NOTHING;

-- Adds sales
INSERT INTO sale (inventory_id, customer_id, sale_date, sale_price)
VALUES
((SELECT inventory_id FROM inventory WHERE vin = '1HGCM82633A004352' LIMIT 1), (SELECT customer_id FROM customer WHERE first_name = 'John' LIMIT 1), '2024-03-10', 27500),
((SELECT inventory_id FROM inventory WHERE vin = '2T1BURHE5JC123456' LIMIT 1), (SELECT customer_id FROM customer WHERE first_name = 'Sarah' LIMIT 1), '2024-05-15', 32500),
((SELECT inventory_id FROM inventory WHERE vin = '1FAFP45X1XF123456' LIMIT 1), (SELECT customer_id FROM customer WHERE first_name = 'Alex' LIMIT 1), '2024-06-20', 45500),
((SELECT inventory_id FROM inventory WHERE vin = 'WBA8D9G54JNU12345' LIMIT 1), (SELECT customer_id FROM customer WHERE first_name = 'Emily' LIMIT 1), '2024-08-01', 50000),
((SELECT inventory_id FROM inventory WHERE vin = '19XFC2F59HE123456' LIMIT 1), (SELECT customer_id FROM customer WHERE first_name = 'Chris' LIMIT 1), '2023-09-12', 25000),
((SELECT inventory_id FROM inventory WHERE vin = 'WDDWK8DB1HF123456' LIMIT 1), (SELECT customer_id FROM customer WHERE first_name = 'Sarah' LIMIT 1), '2024-07-30', 61000),
((SELECT inventory_id FROM inventory WHERE vin = 'JM1NDAD70K0123456' LIMIT 1), (SELECT customer_id FROM customer WHERE first_name = 'John' LIMIT 1), '2025-06-12', 34500)
ON CONFLICT DO NOTHING;

-- Add recent sales data for past-year reports
INSERT INTO vehicle (vin, model_id, plant_id, model_year, color, mileage)
VALUES
('1HGCM82633A99991', (SELECT model_id FROM model WHERE model_name = 'Camry' LIMIT 1), (SELECT plant_id FROM plant WHERE plant_name = 'Dallas Assembly' LIMIT 1), 2026, 'Blue', 15),
('2T1BURHE5JC99992', (SELECT model_id FROM model WHERE model_name = 'RAV4' LIMIT 1), (SELECT plant_id FROM plant WHERE plant_name = 'Dallas Assembly' LIMIT 1), 2026, 'White', 20),
('1FAFP45X1XF99993', (SELECT model_id FROM model WHERE model_name = 'Mustang' LIMIT 1), (SELECT plant_id FROM plant WHERE plant_name = 'Dallas Assembly' LIMIT 1), 2026, 'Red', 10)
ON CONFLICT (vin) DO NOTHING;

INSERT INTO inventory (dealer_id, vin, date_received, date_sold, sticker_price)
VALUES
((SELECT dealer_id FROM dealer WHERE dealer_name = 'Lone Star Auto Group' LIMIT 1), '1HGCM82633A99991', '2026-01-10', '2026-02-05', 31000),
((SELECT dealer_id FROM dealer WHERE dealer_name = 'Lone Star Auto Group' LIMIT 1), '2T1BURHE5JC99992', '2026-01-15', '2026-03-12', 36000),
((SELECT dealer_id FROM dealer WHERE dealer_name = 'DFW Premier Motors' LIMIT 1), '1FAFP45X1XF99993', '2026-02-01', '2026-04-02', 48000)
ON CONFLICT DO NOTHING;

INSERT INTO sale (inventory_id, customer_id, sale_date, sale_price)
VALUES
((SELECT inventory_id FROM inventory WHERE vin = '1HGCM82633A99991' LIMIT 1), (SELECT customer_id FROM customer WHERE first_name = 'John' LIMIT 1), '2026-02-05', 30500),
((SELECT inventory_id FROM inventory WHERE vin = '2T1BURHE5JC99992' LIMIT 1), (SELECT customer_id FROM customer WHERE first_name = 'Sarah' LIMIT 1), '2026-03-12', 35500),
((SELECT inventory_id FROM inventory WHERE vin = '1FAFP45X1XF99993' LIMIT 1), (SELECT customer_id FROM customer WHERE first_name = 'Alex' LIMIT 1), '2026-04-02', 47500)
ON CONFLICT DO NOTHING;