CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    user_id INT,
    description TEXT,
    weight TEXT,
    dimensions TEXT,
    sender_address TEXT,
    receiver_address TEXT,
    payment_method TEXT
);

CREATE TABLE claims (
    id SERIAL PRIMARY KEY,
    user_id INT,
    invoice_number TEXT,
    email TEXT,
    situation_description TEXT,
    requested_amount TEXT,
    photos TEXT
);

CREATE TABLE client_chats (
    id SERIAL PRIMARY KEY,
    user_id INT,
    chat_id INT
);
