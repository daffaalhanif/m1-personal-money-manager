-- =========================================================
-- Capstone M1: Personal Money Manager | Xpense Insight (Schema + Seed Data)
-- Database: m1_capst_money_manager
-- Seed: 10 categories + 100 transactions
-- Composition: OUT=60, IN=40
-- =========================================================

CREATE DATABASE m1_capst_money_manager;
USE m1_capst_money_manager;

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(100) NOT NULL,
  flow ENUM('IN', 'OUT') NOT NULL,
  UNIQUE (category_name)
);

CREATE TABLE transactions (
  trx_id INT AUTO_INCREMENT PRIMARY KEY,
  trx_date DATE NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  flow ENUM('IN','OUT') NOT NULL,
  category_id INT NOT NULL,
  note VARCHAR(255),
  CONSTRAINT fk_transactions_category
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

-- =========================================================
-- Categories (10)
-- Mapping (important):
-- 1 Salary, 2 Freelance, 3 Dividend,
-- 4 Food, 5 Transport, 6 Sport, 7 Investment,
-- 8 Subscription, 9 Books, 10 Utilities
-- =========================================================
INSERT INTO categories (category_name, flow) VALUES
('Salary', 'IN'),
('Freelance', 'IN'),
('Dividend', 'IN'),
('Food', 'OUT'),
('Transport', 'OUT'),
('Sports', 'OUT'),
('Investment', 'OUT'),
('Subscriptions', 'OUT'),
('Books', 'OUT'),
('Utilities', 'OUT');

-- =========================================================
-- Transactions (100 total)
-- IN = 40 (Salary 10 weekly, Freelance 24, Dividend 6)
-- OUT = 60 (Food 22, Transport 15, Sport 8 tennis-only, Investment 7,
--           Subscription 4, Books 2, Utilities 2)
-- =========================================================

INSERT INTO transactions (trx_date, amount, flow, category_id, note) VALUES
-- ======================
-- IN (40)
-- Salary (Weekly) - 10
('2026-01-05', 2000000.00, 'IN', 1, 'Weekly salary'),
('2026-01-12', 2000000.00, 'IN', 1, 'Weekly salary'),
('2026-01-19', 2000000.00, 'IN', 1, 'Weekly salary'),
('2026-01-26', 2000000.00, 'IN', 1, 'Weekly salary'),
('2026-02-02', 2000000.00, 'IN', 1, 'Weekly salary'),
('2026-02-09', 2000000.00, 'IN', 1, 'Weekly salary'),
('2026-02-16', 2000000.00, 'IN', 1, 'Weekly salary'),
('2026-02-23', 2000000.00, 'IN', 1, 'Weekly salary'),
('2026-03-02', 2000000.00, 'IN', 1, 'Weekly salary'),
('2026-03-09', 2000000.00, 'IN', 1, 'Weekly salary'),

-- Freelance - 24
('2026-01-03',  250000.00, 'IN', 2, 'Freelance: quick edit'),
('2026-01-07',  400000.00, 'IN', 2, 'Freelance: consultation'),
('2026-01-10',  600000.00, 'IN', 2, 'Freelance: milestone payout'),
('2026-01-14',  200000.00, 'IN', 2, 'Freelance: minor fix'),
('2026-01-18',  350000.00, 'IN', 2, 'Freelance: content task'),
('2026-01-22',  500000.00, 'IN', 2, 'Freelance: feature add-on'),
('2026-01-28',  300000.00, 'IN', 2, 'Freelance: support fee'),
('2026-02-04',  450000.00, 'IN', 2, 'Freelance: automation script'),
('2026-02-06',  275000.00, 'IN', 2, 'Freelance: revision fee'),
('2026-02-10',  550000.00, 'IN', 2, 'Freelance: maintenance'),
('2026-02-12',  180000.00, 'IN', 2, 'Freelance: small change request'),
('2026-02-14',  320000.00, 'IN', 2, 'Freelance: design improvement'),
('2026-02-18',  500000.00, 'IN', 2, 'Freelance: feature delivery'),
('2026-02-20',  250000.00, 'IN', 2, 'Freelance: quick support'),
('2026-02-24',  650000.00, 'IN', 2, 'Freelance: project milestone'),
('2026-02-26',  150000.00, 'IN', 2, 'Freelance: minor edit'),
('2026-02-28',  420000.00, 'IN', 2, 'Freelance: bug fix'),
('2026-03-03',  380000.00, 'IN', 2, 'Freelance: report + handover'),
('2026-03-05',  700000.00, 'IN', 2, 'Freelance: client retainer'),
('2026-03-06',  220000.00, 'IN', 2, 'Freelance: urgent request'),
('2026-03-08',  260000.00, 'IN', 2, 'Freelance: small task'),
('2026-03-10',  480000.00, 'IN', 2, 'Freelance: integration help'),
('2026-03-12',  340000.00, 'IN', 2, 'Freelance: UI polishing'),
('2026-03-14',  520000.00, 'IN', 2, 'Freelance: maintenance support'),

-- Dividend - 6
('2026-01-15',  120000.00, 'IN', 3, 'Dividend: stock payout'),
('2026-02-05',  150000.00, 'IN', 3, 'Dividend: stock payout'),
('2026-02-19',  90000.00,  'IN', 3, 'Dividend: stock payout'),
('2026-03-01',  110000.00, 'IN', 3, 'Dividend: stock payout'),
('2026-03-11',  130000.00, 'IN', 3, 'Dividend: stock payout'),
('2026-03-15',  100000.00, 'IN', 3, 'Dividend: stock payout'),

-- ======================
-- OUT (60)
-- Food - 22
('2026-01-02',   35000.00, 'OUT', 4, 'Breakfast'),
('2026-01-04',   65000.00, 'OUT', 4, 'Lunch'),
('2026-01-06',   90000.00, 'OUT', 4, 'Dinner'),
('2026-01-08',  175000.00, 'OUT', 4, 'Groceries'),
('2026-01-09',   45000.00, 'OUT', 4, 'Coffee & snack'),
('2026-01-11',  160000.00, 'OUT', 4, 'Weekly groceries'),
('2026-01-13',   85000.00, 'OUT', 4, 'Dinner with friends'),
('2026-01-16',   55000.00, 'OUT', 4, 'Breakfast & coffee'),
('2026-01-20',  210000.00, 'OUT', 4, 'Groceries'),
('2026-01-24',  140000.00, 'OUT', 4, 'Groceries top-up'),
('2026-01-27',   60000.00, 'OUT', 4, 'Coffee & snack'),
('2026-02-01',  130000.00, 'OUT', 4, 'Lunch'),
('2026-02-03',   95000.00, 'OUT', 4, 'Dinner'),
('2026-02-07',  200000.00, 'OUT', 4, 'Weekly groceries'),
('2026-02-11',   70000.00, 'OUT', 4, 'Lunch'),
('2026-02-13',  120000.00, 'OUT', 4, 'Dinner'),
('2026-02-17',  185000.00, 'OUT', 4, 'Groceries'),
('2026-02-21',   50000.00, 'OUT', 4, 'Breakfast'),
('2026-02-25',  110000.00, 'OUT', 4, 'Dinner'),
('2026-03-04',   65000.00, 'OUT', 4, 'Lunch'),
('2026-03-07',  160000.00, 'OUT', 4, 'Weekly groceries'),
('2026-03-13',   90000.00, 'OUT', 4, 'Dinner'),

-- Transport - 15
('2026-01-02',   18000.00, 'OUT', 5, 'Public transport'),
('2026-01-05',   25000.00, 'OUT', 5, 'Ride-hailing'),
('2026-01-07',   22000.00, 'OUT', 5, 'Train ticket'),
('2026-01-10',   30000.00, 'OUT', 5, 'Commute costs'),
('2026-01-12',   42000.00, 'OUT', 5, 'Public transport'),
('2026-01-15',   35000.00, 'OUT', 5, 'Fuel/transport'),
('2026-01-18',   26000.00, 'OUT', 5, 'Ride-hailing'),
('2026-01-23',   32000.00, 'OUT', 5, 'Commute costs'),
('2026-01-29',   45000.00, 'OUT', 5, 'Public transport'),
('2026-02-02',   28000.00, 'OUT', 5, 'Ride-hailing'),
('2026-02-08',   40000.00, 'OUT', 5, 'Public transport'),
('2026-02-14',   22000.00, 'OUT', 5, 'Train ticket'),
('2026-02-20',   30000.00, 'OUT', 5, 'Commute costs'),
('2026-03-02',   42000.00, 'OUT', 5, 'Public transport'),
('2026-03-12',   35000.00, 'OUT', 5, 'Ride-hailing'),

-- Sport (Tennis only) - 8
('2026-01-06',  120000.00, 'OUT', 6, 'Tennis: court rental (1 hour)'),
('2026-01-14',  150000.00, 'OUT', 6, 'Tennis: coaching session (group)'),
('2026-01-22',   65000.00, 'OUT', 6, 'Tennis: balls (can)'),
('2026-02-06',  250000.00, 'OUT', 6, 'Tennis: racket stringing'),
('2026-02-15',   45000.00, 'OUT', 6, 'Tennis: overgrip pack'),
('2026-02-24',  110000.00, 'OUT', 6, 'Tennis: coaching session (private)'),
('2026-03-05',  180000.00, 'OUT', 6, 'Tennis: court rental (90 minutes)'),
('2026-03-14',   90000.00, 'OUT', 6, 'Tennis: training (club session)'),

-- Investment - 7
('2026-01-09',  500000.00, 'OUT', 7, 'Investment: stock top-up'),
('2026-01-25',  300000.00, 'OUT', 7, 'Investment: crypto DCA'),
('2026-02-09',  750000.00, 'OUT', 7, 'Investment: mutual fund DCA'),
('2026-02-23',  600000.00, 'OUT', 7, 'Investment: stock top-up'),
('2026-03-01',  400000.00, 'OUT', 7, 'Investment: bond fund top-up'),
('2026-03-08',  550000.00, 'OUT', 7, 'Investment: crypto DCA'),
('2026-03-15',  650000.00, 'OUT', 7, 'Investment: mutual fund DCA'),

-- Subscription - 4
('2026-01-01',   59000.00, 'OUT', 8, 'Subscription: music streaming'),
('2026-02-01',   59000.00, 'OUT', 8, 'Subscription: music streaming'),
('2026-03-01',   99000.00, 'OUT', 8, 'Subscription: video streaming'),
('2026-03-10',   35000.00, 'OUT', 8, 'Subscription: cloud storage'),

-- Books - 2
('2026-01-17',  125000.00, 'OUT', 9, 'Books: business analysis book'),
('2026-02-27',  150000.00, 'OUT', 9, 'Books: investing book'),

-- Utilities - 2
('2026-01-31',  350000.00, 'OUT', 10, 'Utilities: internet bill'),
('2026-02-28',  420000.00, 'OUT', 10, 'Utilities: electricity bill');
