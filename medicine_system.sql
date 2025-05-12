-- Active: 1746949952149@@127.0.0.1@3306
-- 创建药品分类表
CREATE TABLE Category (
    CategoryID INT PRIMARY KEY AUTO_INCREMENT,
    CategoryName VARCHAR(50) NOT NULL,
    ParentCategoryID INT,
    Description VARCHAR(200),
    FOREIGN KEY (ParentCategoryID) REFERENCES Category(CategoryID)
) ENGINE=InnoDB;

-- 创建供应商表
CREATE TABLE Supplier (
    SupplierID INT PRIMARY KEY AUTO_INCREMENT,
    SupplierName VARCHAR(100) NOT NULL,
    ContactPerson VARCHAR(50),
    Phone VARCHAR(20),
    Address VARCHAR(200),
    Email VARCHAR(50),
    Status TINYINT(1) DEFAULT 1
) ENGINE=InnoDB;

-- 创建客户表
CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerName VARCHAR(100) NOT NULL,
    ContactPerson VARCHAR(50),
    Phone VARCHAR(20),
    Address VARCHAR(200),
    Email VARCHAR(50),
    VIPLevel INT DEFAULT 0,
    Status TINYINT(1) DEFAULT 1
) ENGINE=InnoDB;

-- 创建折扣策略表
CREATE TABLE DiscountPolicy (
    PolicyID INT PRIMARY KEY AUTO_INCREMENT,
    PolicyName VARCHAR(50) NOT NULL,
    DiscountType INT NOT NULL,
    DiscountValue DECIMAL(5,2) NOT NULL,
    StartDate DATE,
    EndDate DATE,
    Description VARCHAR(200),
    Status TINYINT(1) DEFAULT 1
) ENGINE=InnoDB;

-- 创建药品表
CREATE TABLE Medicine (
    MedicineID INT PRIMARY KEY AUTO_INCREMENT,
    MedicineCode VARCHAR(20) NOT NULL UNIQUE,
    MedicineName VARCHAR(100) NOT NULL,
    CategoryID INT NOT NULL,
    SupplierID INT NOT NULL,
    Specification VARCHAR(50),
    Unit VARCHAR(10),
    PurchasePrice DECIMAL(10,2) NOT NULL,
    RetailPrice DECIMAL(10,2) NOT NULL,
    ProductionDate DATE,
    ExpiryDate DATE,
    BatchNumber VARCHAR(50),
    StockWarningLevel INT,
    MaxStockLevel INT,
    Status TINYINT(1) DEFAULT 1,
    FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID),
    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID)
) ENGINE=InnoDB;

-- 创建库存表
CREATE TABLE Inventory (
    InventoryID INT PRIMARY KEY AUTO_INCREMENT,
    MedicineID INT NOT NULL,
    CurrentQuantity INT NOT NULL DEFAULT 0,
    LastUpdateDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Warehouse VARCHAR(50),
    Location VARCHAR(50),
    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID),
    UNIQUE (MedicineID, Warehouse)
) ENGINE=InnoDB;

-- 创建采购单主表
CREATE TABLE PurchaseOrder (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    OrderNumber VARCHAR(50) NOT NULL UNIQUE,
    SupplierID INT NOT NULL,
    OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    ExpectedArrivalDate DATE,
    ActualArrivalDate DATE,
    OrderStatus INT NOT NULL DEFAULT 1,
    CreatedBy VARCHAR(50),
    Remarks VARCHAR(200),
    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID)
) ENGINE=InnoDB;

-- 创建销售单主表
CREATE TABLE SalesOrder (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    OrderNumber VARCHAR(50) NOT NULL UNIQUE,
    CustomerID INT NOT NULL,
    OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    PolicyID INT,
    TotalAmount DECIMAL(10,2) NOT NULL,
    DiscountAmount DECIMAL(10,2) DEFAULT 0,
    NetAmount DECIMAL(10,2) NOT NULL,
    OrderStatus INT NOT NULL DEFAULT 1,
    CreatedBy VARCHAR(50),
    Remarks VARCHAR(200),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (PolicyID) REFERENCES DiscountPolicy(PolicyID)
) ENGINE=InnoDB;

-- 创建过期药品记录表
CREATE TABLE ExpiredMedicine (
    ExpiryID INT PRIMARY KEY AUTO_INCREMENT,
    MedicineID INT NOT NULL,
    BatchNumber VARCHAR(50),
    ExpiryDate DATE NOT NULL,
    Quantity INT NOT NULL,
    DisposalDate DATE,
    DisposalMethod VARCHAR(50),
    HandledBy VARCHAR(50),
    Remarks VARCHAR(200),
    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID)
) ENGINE=InnoDB;

-- 创建药品损耗记录表
CREATE TABLE Wastage (
    WastageID INT PRIMARY KEY AUTO_INCREMENT,
    MedicineID INT NOT NULL,
    Quantity INT NOT NULL,
    WastageDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Reason VARCHAR(100) NOT NULL,
    HandledBy VARCHAR(50),
    Remarks VARCHAR(200),
    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID)
) ENGINE=InnoDB;

-- 创建库存盘点表
CREATE TABLE InventoryCheck (
    CheckID INT PRIMARY KEY AUTO_INCREMENT,
    CheckNumber VARCHAR(50) NOT NULL UNIQUE,
    CheckDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Warehouse VARCHAR(50),
    CheckedBy VARCHAR(50),
    Status INT DEFAULT 1,
    Remarks VARCHAR(200)
) ENGINE=InnoDB;