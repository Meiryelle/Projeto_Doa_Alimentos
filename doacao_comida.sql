CREATE DATABASE doacao_comida;

USE doacao_comida;

CREATE TABLE pessoa_fisica (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100),
    telefone VARCHAR(20),
    localizacao VARCHAR(100)
);

CREATE TABLE ong (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    responsavel VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(15) NOT NULL
);

CREATE TABLE restaurante (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    endereco VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(15) NOT NULL
);

CREATE TABLE alertas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurante_id INT NOT NULL,
    tipo VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    localizacao VARCHAR(255) NOT NULL,
    numero VARCHAR(15) NOT NULL,
    FOREIGN KEY (restaurante_id) REFERENCES restaurante(id)
);
