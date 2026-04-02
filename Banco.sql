DROP DATABASE imobiliaria;
CREATE DATABASE imobiliaria;

USE imobiliaria;

CREATE TABLE modalidades (
	id INT PRIMARY KEY AUTO_INCREMENT,
    modalidade VARCHAR(50) NOT NULL
);

CREATE TABLE tipos (
	id INT PRIMARY KEY AUTO_INCREMENT,
    tipo VARCHAR(50) NOT NULL
);

CREATE TABLE finalidades (
	id INT PRIMARY KEY AUTO_INCREMENT,
    finalidade VARCHAR(50) NOT NULL
);

CREATE TABLE utilizacao (
	id INT PRIMARY KEY AUTO_INCREMENT,
    utilizacao VARCHAR(50) NOT NULL
);

CREATE TABLE imoveis (
	id INT PRIMARY KEY AUTO_INCREMENT,
    descricao VARCHAR(3000),
    cidade VARCHAR(50),
    localizacao VARCHAR(300),
    rua VARCHAR(250),
    bairro VARCHAR(150),
    cep VARCHAR(8),
    numero VARCHAR(8),
    area_total INT,
    area_construida INT,
    valor INT,
    modalidade_id INT,
    FOREIGN KEY (modalidade_id) REFERENCES modalidades(id),
    tipo_id INT,
    FOREIGN KEY (tipo_id) REFERENCES tipos(id),
    finalidade_id INT,
    FOREIGN KEY (finalidade_id) REFERENCES finalidades(id),
    utilizacao_id INT,
    FOREIGN KEY (utilizacao_id) REFERENCES utilizacao(id),
    quantidade_suites INT,
	quantidade_quartos INT,
	quantidade_banheiros INT,
	quantidade_vagas INT,
	quantidade_salas INT,
	quantidade_cozinhas INT,
	quantidade_churrasqueira INT,
	quantidade_escritorio INT,
    data_inserido DATE,
    data_removido DATE,
    link VARCHAR(300)
);

