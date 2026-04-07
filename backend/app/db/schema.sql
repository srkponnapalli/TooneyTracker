-- Users
CREATE TABLE IF NOT EXISTS users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       TEXT UNIQUE NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Institutions (Banks)
CREATE TABLE IF NOT EXISTS institutions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID REFERENCES users(id) ON DELETE CASCADE,
    plaid_item_id       TEXT UNIQUE NOT NULL,
    access_token        TEXT NOT NULL,
    institution_id      TEXT NOT NULL,
    institution_name    TEXT NOT NULL,
    cursor              TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    last_synced_at      TIMESTAMPTZ
);

-- Accounts
CREATE TABLE IF NOT EXISTS accounts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id      UUID REFERENCES institutions(id) ON DELETE CASCADE,
    plaid_account_id    TEXT UNIQUE NOT NULL,
    name                TEXT NOT NULL,
    type                TEXT NOT NULL,
    subtype             TEXT,
    current_balance     NUMERIC(12,2),
    available_balance   NUMERIC(12,2),
    currency            TEXT DEFAULT 'CAD',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Categories
CREATE TABLE IF NOT EXISTS categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT UNIQUE NOT NULL,
    parent      TEXT,
    is_custom   BOOLEAN DEFAULT FALSE
);

-- Transactions
CREATE TABLE IF NOT EXISTS transactions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id              UUID REFERENCES accounts(id) ON DELETE CASCADE,
    plaid_transaction_id    TEXT UNIQUE NOT NULL,
    amount                  NUMERIC(12,2) NOT NULL,
    currency                TEXT DEFAULT 'CAD',
    merchant_name           TEXT,
    raw_name                TEXT NOT NULL,
    category_id             UUID REFERENCES categories(id),
    date                    DATE NOT NULL,
    pending                 BOOLEAN DEFAULT FALSE,
    payment_channel         TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Budgets
CREATE TABLE IF NOT EXISTS budgets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id     UUID REFERENCES categories(id),
    month           DATE NOT NULL,
    limit_amount    NUMERIC(12,2) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, category_id, month)
);