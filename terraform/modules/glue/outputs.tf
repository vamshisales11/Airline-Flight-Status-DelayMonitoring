output "glue_database_name" {
  value = aws_glue_catalog_database.flight_db.name
}

output "raw_crawler_name" {
  value = aws_glue_crawler.raw_flights_crawler.name
}

output "processed_crawler_name" {
  value = aws_glue_crawler.processed_flights_crawler.name
}
