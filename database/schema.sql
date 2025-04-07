IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
CREATE TABLE users (
  id INT IDENTITY(1,1) PRIMARY KEY,
  customer_id NVARCHAR(100) UNIQUE NOT NULL
);

