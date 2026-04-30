Automobile Company Database Project
CSCE 4350 – Fundamentals of Database Systems

⸻

Project Overview

This project designs and implements a relational database system for an automobile company. The system models core operations including vehicle production, suppliers, parts, dealerships, inventory management, customers, and sales.

The goal is to create a normalized database schema, support analytical queries, and provide basic user interfaces for interacting with the data.

⸻

Repository Contents

setup_schema.sql
Contains all SQL statements to create database tables, constraints, and relationships.

cli.py
Command-line interface for interacting with the database. Supports basic operations such as viewing inventory, searching vehicles, and recording sales.

Group8_ER_Diagram.drawio.png
Entity-Relationship diagram representing the conceptual design of the database.

Group8_ER_Diagram.drawio.xml
Editable version of the ER diagram.

plantuml_export.puml
Alternative diagram representation.

Checkpoint2_Group8.docx
Checkpoint 2 submission document containing relational schema, interface descriptions, and development schedule.

⸻

Database Features

Relational schema designed using normalization principles up to Third Normal Form.

Primary and foreign key constraints ensure referential integrity.

Support for vehicle tracking through manufacturing, inventory, and sales lifecycle.

Supplier and parts relationships modeled to support defect tracing queries.

Sales data supports analytical queries such as trends, revenue, and performance.

⸻

User Interfaces

Database Administrator
Direct database interaction for managing tables and data.

Vehicle Locator
Search vehicles by VIN and view full details including model, brand, and availability.

Sales Interface
Record and view vehicle sales transactions.

Marketing / Analytics
Supports analytical queries such as sales trends, top brands, and inventory performance.

⸻

How to Run:

	1.	Open PostgreSQL
	
	2.	Run setup_schema.sql to create all tables
	
	3.	Run cli.py to start the command-line interface

Ensure database connection details in cli.py match your local setup.

⸻

Development Status

Checkpoint 2 completed
	•	Relational schema finalized
	•	ER diagram created
	•	CLI prototype implemented
	•	Documentation prepared

Next steps include query implementation, interface expansion, and final integration.

⸻

Team Members
Jakob saunders
Achintya Yalamati
Justin Zeller
Abhiram Makkapati
