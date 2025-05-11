-- 创建药品分类表
CREATE TABLE Category (
    CategoryID INT PRIMARY KEY IDENTITY(1,1),
    CategoryName VARCHAR(50) NOT NULL,
    ParentCategoryID INT,
    Description VARCHAR(200),
    FOREIGN KEY (ParentCategoryID) REFERENCES Category(CategoryID)
);

-- 创建供应商表
CREATE TABLE Supplier (
    SupplierID INT PRIMARY KEY IDENTITY(1,1),
    SupplierName VARCHAR(100) NOT NULL,
    ContactPerson VARCHAR(50),
    Phone VARCHAR(20),
    Address VARCHAR(200),
    Email VARCHAR(50),
    Status BIT DEFAULT 1
);

-- 创建药品表
CREATE TABLE Medicine (
    MedicineID INT PRIMARY KEY IDENTITY(1,1),
    MedicineCode VARCHAR(20) UNIQUE NOT NULL,
    MedicineName VARCHAR(100) NOT NULL,
    CategoryID INT NOT NULL,
    SupplierID INT NOT NULL,
    Specification VARCHAR(50),  -- 规格
    Unit VARCHAR(10),           -- 单位
    PurchasePrice DECIMAL(10,2) NOT NULL,
    RetailPrice DECIMAL(10,2) NOT NULL,
    ProductionDate DATE,
    ExpiryDate DATE,
    BatchNumber VARCHAR(50),
    StockWarningLevel INT,     -- 库存预警值
    MaxStockLevel INT,         -- 最大库存值
    Status BIT DEFAULT 1,
    FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID),
    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID)
);

-- 创建客户表
CREATE TABLE Customer(
    CustomerID INT PRIMARY KEY IDENTITY(1,1),
    CustomerName VARCHAR(100) NOT NULL,
    ContactPerson VARCHAR(50),
    Phone VARCHAR(20),
    Address VARCHAR(200),
    Email VARCHAR(50),
    VIPLevel INT DEFAULT 0,    -- VIP等级
    Status BIT DEFAULT 1
);

-- 创建折扣策略表
CREATE TABLE DiscountPolicy (
    PolicyID INT PRIMARY KEY IDENTITY(1,1),
    PolicyName VARCHAR(50) NOT NULL,
    DiscountType INT NOT NULL,  -- 1=百分比 2=固定金额
    DiscountValue DECIMAL(5,2) NOT NULL,
    StartDate DATE,
    EndDate DATE,
    Description VARCHAR(200),
    Status BIT DEFAULT 1
);

-- 创建库存表
CREATE TABLE Inventory (
    InventoryID INT PRIMARY KEY IDENTITY(1,1),
    MedicineID INT NOT NULL,
    CurrentQuantity INT NOT NULL DEFAULT 0,
    LastUpdateDate DATETIME DEFAULT GETDATE(),
    Warehouse VARCHAR(50),
    Location VARCHAR(50),      -- 货架位置
    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID),
    UNIQUE (MedicineID, Warehouse)
);

-- 创建采购单主表
CREATE TABLE PurchaseOrder (
    OrderID INT PRIMARY KEY IDENTITY(1,1),
    OrderNumber VARCHAR(50) UNIQUE NOT NULL,
    SupplierID INT NOT NULL,
    OrderDate DATETIME DEFAULT GETDATE(),
    ExpectedArrivalDate DATE,
    ActualArrivalDate DATE,
    OrderStatus INT NOT NULL DEFAULT 1,  -- 1=已下单 2=已到货 3=已验收 4=已入库 5=已取消
    CreatedBy VARCHAR(50),
    Remarks VARCHAR(200),
    FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID)
);

-- 创建销售单主表
CREATE TABLE SalesOrder (
    OrderID INT PRIMARY KEY IDENTITY(1,1),
    OrderNumber VARCHAR(50) UNIQUE NOT NULL,
    CustomerID INT NOT NULL,
    OrderDate DATETIME DEFAULT GETDATE(),
    PolicyID INT,           -- 折扣策略
    TotalAmount DECIMAL(10,2) NOT NULL,
    DiscountAmount DECIMAL(10,2) DEFAULT 0,
    NetAmount DECIMAL(10,2) NOT NULL,
    OrderStatus INT NOT NULL DEFAULT 1,  -- 1=已下单 2=已出库 3=已完成 4=已取消
    CreatedBy VARCHAR(50),
    Remarks VARCHAR(200),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (PolicyID) REFERENCES DiscountPolicy(PolicyID)
);


-- 创建过期药品记录表
CREATE TABLE ExpiredMedicine (
    ExpiryID INT PRIMARY KEY IDENTITY(1,1),
    MedicineID INT NOT NULL,
    BatchNumber VARCHAR(50),
    ExpiryDate DATE NOT NULL,
    Quantity INT NOT NULL,
    DisposalDate DATE,
    DisposalMethod VARCHAR(50),
    HandledBy VARCHAR(50),
    Remarks VARCHAR(200),
    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID)
);

-- 创建药品损耗记录表
CREATE TABLE Wastage (
    WastageID INT PRIMARY KEY IDENTITY(1,1),
    MedicineID INT NOT NULL,
    Quantity INT NOT NULL,
    WastageDate DATETIME DEFAULT GETDATE(),
    Reason VARCHAR(100) NOT NULL,
    HandledBy VARCHAR(50),
    Remarks VARCHAR(200),
    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID)
);

-- 创建库存盘点表
CREATE TABLE InventoryCheck (
    CheckID INT PRIMARY KEY IDENTITY(1,1),
    CheckNumber VARCHAR(50) UNIQUE NOT NULL,
    CheckDate DATETIME DEFAULT GETDATE(),
    Warehouse VARCHAR(50),
    CheckedBy VARCHAR(50),
    Status INT DEFAULT 1,  -- 1=进行中 2=已完成
    Remarks VARCHAR(200)
);
