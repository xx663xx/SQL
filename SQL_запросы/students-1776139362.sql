CREATE TABLE IF NOT EXISTS `уровни` (
	`id_ровня` integer primary key NOT NULL UNIQUE,
	`название` TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS `направления` (
	`id_направления` integer primary key NOT NULL UNIQUE,
	`название` TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS `типы` (
	`id_типа` integer primary key NOT NULL UNIQUE,
	`название` TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS `студенты` (
	`id_студента` integer primary key NOT NULL UNIQUE,
	`id_уровня` INTEGER NOT NULL,
	`id_направления` INTEGER NOT NULL,
	`id_типа` INTEGER NOT NULL,
	`фамилия` TEXT NOT NULL,
	`имя` TEXT NOT NULL,
	`средний_балл` REAL NOT NULL,
FOREIGN KEY(`id_уровня`) REFERENCES `уровни`(`id_ровня`),
FOREIGN KEY(`id_направления`) REFERENCES `направления`(`id_направления`),
FOREIGN KEY(`id_типа`) REFERENCES `типы`(`id_типа`)
);