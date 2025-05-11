-- torch.request definition

--CREATE TABLE `request` (
--  `id` bigint NOT NULL AUTO_INCREMENT,
--  `create_at` timestamp NOT NULL,
--  `status` varchar(100) DEFAULT NULL,
--  PRIMARY KEY (`id`)
--) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE summary_request (
  id bigint NOT NULL AUTO_INCREMENT,
  req_id char(36) NOT NULL DEFAULT (UUID()),
  create_at timestamp NOT NULL,
  status varchar(100) DEFAULT NULL,
  github_url TEXT DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (req_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
