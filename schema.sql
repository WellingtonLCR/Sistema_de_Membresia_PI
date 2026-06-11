CREATE DATABASE IF NOT EXISTS igreja_membros
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE igreja_membros;

CREATE TABLE IF NOT EXISTS cargos (
    id_cargo BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
    descricao VARCHAR(255),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS celulas (
    id_celula BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    lider VARCHAR(255),
    dia_semana VARCHAR(20),
    horario TIME,
    endereco VARCHAR(255),
    status ENUM('Ativa', 'Inativa') DEFAULT 'Ativa',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS membros (
    id_membro BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) UNIQUE,
    data_nascimento DATE,
    email VARCHAR(255) UNIQUE,
    celular VARCHAR(20),
    cep VARCHAR(9),
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado CHAR(2),
    data_batismo DATE,
    data_ingresso DATE DEFAULT (CURRENT_DATE),
    status ENUM('Ativo', 'Inativo', 'Visitante', 'Transferido') DEFAULT 'Ativo',
    cargo_id BIGINT UNSIGNED,
    celula_id BIGINT UNSIGNED,
    observacoes TEXT,
    senha VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_membro_cargo FOREIGN KEY (cargo_id) REFERENCES cargos (id_cargo),
    CONSTRAINT fk_membro_celula FOREIGN KEY (celula_id) REFERENCES celulas (id_celula)
);

CREATE TABLE IF NOT EXISTS contribuicoes (
    id_contribuicao BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    membro_id BIGINT UNSIGNED NOT NULL,
    tipo ENUM('Dízimo', 'Oferta', 'Missões', 'Construção', 'Outros') NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data_pagamento DATE NOT NULL DEFAULT (CURRENT_DATE),
    forma_pagamento ENUM('Dinheiro', 'PIX', 'Cartão', 'Transferência') DEFAULT 'Dinheiro',
    observacao VARCHAR(255),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_contribuicao_membro FOREIGN KEY (membro_id) REFERENCES membros (id_membro)
);
