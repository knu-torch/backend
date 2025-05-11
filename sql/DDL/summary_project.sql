-- torch.summary_project definition

CREATE TABLE `summary_project` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `create_at` timestamp NOT NULL,
  `title` TEXT DEFAULT NULL,
  `libs` TEXT DEFAULT NULL,
  `deploy_info` TEXT DEFAULT NULL,
  `req_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `summary_project_request_FK` (`req_id`),
  CONSTRAINT `summary_project_request_FK` FOREIGN KEY (`req_id`) REFERENCES `summary_request` (`req_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;