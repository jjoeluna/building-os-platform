# =============================================================================
# NETWORKING AND VPC - BuildingOS Platform
# =============================================================================
# Purpose: Define VPC, subnets, route tables, NAT gateway, security groups, NACLs,
# and VPC Endpoints for AWS service access from private subnets.
#
# Variable usage:
# - local.resource_prefix: naming prefix (bos-${var.environment}) applied to all resources
# - data.aws_region.current.id: region identifier used in VPC Endpoint service names
# - data.aws_availability_zones.available.names: AZ list used for multi-AZ subnets
#
# CIDR allocation strategy:
# - VPC: 10.0.0.0/16
# - Public subnets: 10.0.1.0/24 and 10.0.2.0/24 (mapped to first two AZs)
# - Private subnets: 10.0.10.0/24 and 10.0.11.0/24 (mapped to first two AZs)
#
# VPC Endpoints (cost and security optimization):
# - Gateway: S3, DynamoDB
# - Interface: Secrets Manager, Lambda, SNS, Bedrock Runtime, KMS
#
# Outputs:
# - vpc_id, vpc_cidr_block, public_subnet_ids, private_subnet_ids,
#   nat_gateway_id, lambda_security_group_id, api_gateway_security_group_id
# =============================================================================

# -----------------------------------------------------------------------------
# VPC Configuration
# -----------------------------------------------------------------------------

# Main VPC for the BuildingOS platform
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-vpc"
    Type      = "VPC"
    Component = "Networking"
    Function  = "Main VPC"
    ManagedBy = "Terraform"
  })
}

# Internet Gateway for public subnets
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-igw"
    Type      = "Internet Gateway"
    Component = "Networking"
    Function  = "Internet Access"
    ManagedBy = "Terraform"
  })
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.main]

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-nat-eip"
    Type      = "Elastic IP"
    Component = "Networking"
    Function  = "NAT Gateway"
    ManagedBy = "Terraform"
  })
}

# NAT Gateway for private subnets
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-nat"
    Type      = "NAT Gateway"
    Component = "Networking"
    Function  = "Private Subnet Access"
    ManagedBy = "Terraform"
  })

  depends_on = [aws_internet_gateway.main]
}

# -----------------------------------------------------------------------------
# Subnets Configuration
# -----------------------------------------------------------------------------

# Public subnets (for NAT Gateway and Load Balancers)
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-public-${data.aws_availability_zones.available.names[count.index]}"
    Type      = "Subnet"
    Component = "Networking"
    Function  = "Public Subnet"
    Tier      = "Public"
    AZ        = data.aws_availability_zones.available.names[count.index]
    ManagedBy = "Terraform"
  })
}

# Private subnets (for Lambda functions and other resources)
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-private-${data.aws_availability_zones.available.names[count.index]}"
    Type      = "Subnet"
    Component = "Networking"
    Function  = "Private Subnet"
    Tier      = "Private"
    AZ        = data.aws_availability_zones.available.names[count.index]
    ManagedBy = "Terraform"
  })
}

# -----------------------------------------------------------------------------
# Route Tables
# -----------------------------------------------------------------------------

# Public route table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-public-rt"
    Type      = "Route Table"
    Component = "Networking"
    Function  = "Public Routes"
    ManagedBy = "Terraform"
  })
}

# Private route table
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-private-rt"
    Type      = "Route Table"
    Component = "Networking"
    Function  = "Private Routes"
    ManagedBy = "Terraform"
  })
}

# Route table associations for public subnets
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Route table associations for private subnets
resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# -----------------------------------------------------------------------------
# Security Groups
# -----------------------------------------------------------------------------

# Default security group for Lambda functions
resource "aws_security_group" "lambda" {
  name        = "${local.resource_prefix}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.main.id

  # Allow inbound HTTPS traffic for VPC Endpoints (SNS, etc.)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  # Allow Lambda to access the internet (for AWS services)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-lambda-sg"
    Type      = "Security Group"
    Component = "Security"
    Function  = "Lambda Access"
    ManagedBy = "Terraform"
  })
}

# Security group for API Gateway (if needed in VPC)
resource "aws_security_group" "api_gateway" {
  name        = "${local.resource_prefix}-api-gateway-sg"
  description = "Security group for API Gateway"
  vpc_id      = aws_vpc.main.id

  # Allow inbound HTTP traffic
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow inbound HTTPS traffic
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-api-gateway-sg"
    Type      = "Security Group"
    Component = "Security"
    Function  = "API Gateway Access"
    ManagedBy = "Terraform"
  })
}

# Security group for database access (if needed)
resource "aws_security_group" "database" {
  name        = "${local.resource_prefix}-database-sg"
  description = "Security group for database access"
  vpc_id      = aws_vpc.main.id

  # Allow inbound traffic from Lambda security group
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }

  # Allow inbound traffic from Lambda security group (PostgreSQL)
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
  }

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-database-sg"
    Type      = "Security Group"
    Component = "Security"
    Function  = "Database Access"
    ManagedBy = "Terraform"
  })
}

# -----------------------------------------------------------------------------
# Network ACLs
# -----------------------------------------------------------------------------

# Default NACL for public subnets
resource "aws_network_acl" "public" {
  vpc_id = aws_vpc.main.id

  # Allow inbound HTTP traffic
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 80
    to_port    = 80
  }

  # Allow inbound HTTPS traffic
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  # Allow inbound ephemeral ports
  ingress {
    protocol   = "tcp"
    rule_no    = 120
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  # Allow all outbound traffic
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 65535
  }

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-public-nacl"
    Type      = "Network ACL"
    Component = "Security"
    Function  = "Public Access Control"
    ManagedBy = "Terraform"
  })
}

# Default NACL for private subnets
resource "aws_network_acl" "private" {
  vpc_id = aws_vpc.main.id

  # Allow inbound traffic from public subnets
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = aws_subnet.public[0].cidr_block
    from_port  = 0
    to_port    = 65535
  }

  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = aws_subnet.public[1].cidr_block
    from_port  = 0
    to_port    = 65535
  }

  # Allow inbound ephemeral ports
  ingress {
    protocol   = "tcp"
    rule_no    = 120
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  # Allow all outbound traffic
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 65535
  }

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-private-nacl"
    Type      = "Network ACL"
    Component = "Security"
    Function  = "Private Access Control"
    ManagedBy = "Terraform"
  })
}

# NACL associations for public subnets
resource "aws_network_acl_association" "public" {
  count          = 2
  network_acl_id = aws_network_acl.public.id
  subnet_id      = aws_subnet.public[count.index].id
}

# NACL associations for private subnets
resource "aws_network_acl_association" "private" {
  count          = 2
  network_acl_id = aws_network_acl.private.id
  subnet_id      = aws_subnet.private[count.index].id
}

# -----------------------------------------------------------------------------
# VPC Endpoints (for AWS services)
# -----------------------------------------------------------------------------

# VPC Endpoint for S3 (to avoid NAT Gateway costs)
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${data.aws_region.current.id}.s3"

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-s3-endpoint"
    Type      = "VPC Endpoint"
    Component = "Networking"
    Function  = "S3 Access"
    ManagedBy = "Terraform"
  })
}

# VPC Endpoint for DynamoDB
resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${data.aws_region.current.id}.dynamodb"

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-dynamodb-endpoint"
    Type      = "VPC Endpoint"
    Component = "Networking"
    Function  = "DynamoDB Access"
    ManagedBy = "Terraform"
  })
}

# VPC Endpoint for Secrets Manager
# Purpose: Private secret retrieval from private subnets without NAT/IGW
resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.id}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.lambda.id]
  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-secretsmanager-endpoint"
    Type      = "VPC Endpoint"
    Component = "Networking"
    Function  = "Secrets Manager Access"
    ManagedBy = "Terraform"
  })
}

# VPC Endpoint for Lambda
# Purpose: Private access to Lambda control-plane APIs from private subnets
resource "aws_vpc_endpoint" "lambda" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.id}.lambda"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.lambda.id]
  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-lambda-endpoint"
    Type      = "VPC Endpoint"
    Component = "Networking"
    Function  = "Lambda Access"
    ManagedBy = "Terraform"
  })
}

# VPC Endpoint for SNS
# Purpose: Private publish/subscribe access for event bus from private subnets
resource "aws_vpc_endpoint" "sns" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.id}.sns"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.lambda.id]
  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-sns-endpoint"
    Type      = "VPC Endpoint"
    Component = "Networking"
    Function  = "SNS Access"
    ManagedBy = "Terraform"
  })
}

# VPC Endpoint for Bedrock
# Purpose: Private model invocation for Bedrock Runtime from private subnets
resource "aws_vpc_endpoint" "bedrock" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.id}.bedrock-runtime"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.lambda.id]
  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-bedrock-endpoint"
    Type      = "VPC Endpoint"
    Component = "Networking"
    Function  = "Bedrock Access"
    ManagedBy = "Terraform"
  })
}

# VPC Endpoint for KMS
# Purpose: Private key management and encryption API access from private subnets
resource "aws_vpc_endpoint" "kms" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.id}.kms"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.lambda.id]
  private_dns_enabled = true

  tags = merge(local.common_tags, {
    Name      = "${local.resource_prefix}-kms-endpoint"
    Type      = "VPC Endpoint"
    Component = "Networking"
    Function  = "KMS Access"
    ManagedBy = "Terraform"
  })
}

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "nat_gateway_id" {
  description = "The ID of the NAT Gateway"
  value       = aws_nat_gateway.main.id
}

output "lambda_security_group_id" {
  description = "The ID of the Lambda security group"
  value       = aws_security_group.lambda.id
}

output "api_gateway_security_group_id" {
  description = "The ID of the API Gateway security group"
  value       = aws_security_group.api_gateway.id
}
