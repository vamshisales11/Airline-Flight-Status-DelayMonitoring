resource "aws_kinesis_stream" "flight_events" {
  name             = "airline-delay-monitoring-${var.environment}-flight-stream"
  shard_count      = 1  # 1 shard for a personal/small project; scale up for production.
  retention_period = 24 # hours to retain data

  tags = {
    Project     = "airline-delay-monitoring"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
