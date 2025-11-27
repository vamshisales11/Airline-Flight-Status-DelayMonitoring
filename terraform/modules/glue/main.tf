resource "aws_glue_catalog_database" "flight_db" {
  name = "airline_delay_monitoring_${var.environment}_db"

  tags = {
    Project     = "airline-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Crawler for RAW data
resource "aws_glue_crawler" "raw_flights_crawler" {
  name         = "airline-delay-monitoring-${var.environment}-raw-crawler"
  role         = var.glue_role_arn
  database_name = aws_glue_catalog_database.flight_db.name

  s3_target {
    path = "s3://${var.raw_bucket_name}/"
  }

  schedule = "cron(0 2 * * ? *)" # optional: run daily at 02:00 UTC

  tags = {
    Project     = "airline-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Crawler for PROCESSED data
resource "aws_glue_crawler" "processed_flights_crawler" {
  name         = "airline-delay-monitoring-${var.environment}-processed-crawler"
  role         = var.glue_role_arn
  database_name = aws_glue_catalog_database.flight_db.name

  s3_target {
    path = "s3://${var.processed_bucket_name}/"
  }

  schedule = "cron(30 2 * * ? *)" # optional: run daily at 02:30 UTC

  tags = {
    Project     = "airline-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
    