CREATE TABLE IF NOT EXISTS invoices (
    user_id INTEGER,
    description TEXT,
    weight TEXT,
    dimensions TEXT,
    sender_address TEXT,
    receiver_address TEXT,
    payment_method TEXT
);

CREATE TABLE IF NOT EXISTS claims (
    user_id INTEGER,
    invoice_number TEXT,
    email TEXT,
    situation_description TEXT,
    requested_amount TEXT,
    photos TEXT
);