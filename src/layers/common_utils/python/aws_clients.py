# =============================================================================
# BuildingOS Platform - Common AWS Clients Utilities
# =============================================================================
#
# **Purpose:** Centralized AWS client initialization and management for Lambda functions
# **Scope:** Provides standardized AWS client setup with optimal performance patterns
# **Usage:** Import and use pre-configured AWS clients across all Lambda functions
#
# **Key Features:**
# - Singleton pattern for client reuse across Lambda invocations
# - Optimized initialization outside handler for better cold start performance
# - Consistent error handling and logging configuration
# - VPC-aware client configuration for secure private subnet execution
#
# **Dependencies:** boto3 (managed by Lambda layer)
# **Integration:** Used by all BuildingOS Lambda functions for AWS service access
#
# =============================================================================

import boto3
import os
from typing import Optional

# =============================================================================
# AWS Client Singletons - Initialized once per Lambda container
# =============================================================================


class AWSClients:
    """
    Singleton AWS client manager for optimal Lambda performance

    Provides centralized AWS client initialization following AWS best practices:
    - Clients initialized outside handler for container reuse
    - Lazy loading for memory efficiency
    - Consistent configuration across all functions
    """

    _dynamodb_resource: Optional[boto3.resource] = None
    _dynamodb_client: Optional[boto3.client] = None
    _sns_client: Optional[boto3.client] = None
    _lambda_client: Optional[boto3.client] = None
    _bedrock_client: Optional[boto3.client] = None
    _events_client: Optional[boto3.client] = None
    _apigateway_client: Optional[boto3.client] = None

    @classmethod
    def get_dynamodb_resource(cls) -> boto3.resource:
        """
        Get DynamoDB resource with optimal configuration

        Returns:
            boto3.resource: Configured DynamoDB resource for table operations
        """
        if cls._dynamodb_resource is None:
            cls._dynamodb_resource = boto3.resource("dynamodb")
        return cls._dynamodb_resource

    @classmethod
    def get_dynamodb_client(cls) -> boto3.client:
        """
        Get DynamoDB client for low-level operations

        Returns:
            boto3.client: Configured DynamoDB client for advanced operations
        """
        if cls._dynamodb_client is None:
            cls._dynamodb_client = boto3.client("dynamodb")
        return cls._dynamodb_client

    @classmethod
    def get_sns_client(cls) -> boto3.client:
        """
        Get SNS client for event-driven communication

        Returns:
            boto3.client: Configured SNS client for publish/subscribe operations
        """
        if cls._sns_client is None:
            cls._sns_client = boto3.client("sns")
        return cls._sns_client

    @classmethod
    def get_lambda_client(cls) -> boto3.client:
        """
        Get Lambda client for function invocations (legacy support)

        Returns:
            boto3.client: Configured Lambda client for direct invocations
        """
        if cls._lambda_client is None:
            cls._lambda_client = boto3.client("lambda")
        return cls._lambda_client

    @classmethod
    def get_bedrock_client(cls) -> boto3.client:
        """
        Get Bedrock client for AI/ML operations

        Returns:
            boto3.client: Configured Bedrock runtime client for AI inference
        """
        if cls._bedrock_client is None:
            cls._bedrock_client = boto3.client("bedrock-runtime")
        return cls._bedrock_client

    @classmethod
    def get_events_client(cls) -> boto3.client:
        """
        Get EventBridge client for event scheduling

        Returns:
            boto3.client: Configured EventBridge client for event management
        """
        if cls._events_client is None:
            cls._events_client = boto3.client("events")
        return cls._events_client

    @classmethod
    def get_apigateway_client(cls) -> boto3.client:
        """
        Get API Gateway Management client for WebSocket operations

        Returns:
            boto3.client: Configured API Gateway client for WebSocket management
        """
        if cls._apigateway_client is None:
            # For WebSocket API management - endpoint configured per function
            cls._apigateway_client = boto3.client("apigatewaymanagementapi")
        return cls._apigateway_client


# =============================================================================
# Convenience Functions - Direct access to common clients
# =============================================================================


def get_dynamodb() -> boto3.resource:
    """Convenience function to get DynamoDB resource"""
    return AWSClients.get_dynamodb_resource()


def get_dynamodb_resource() -> boto3.resource:
    """Convenience function to get DynamoDB resource (alias for compatibility)"""
    return AWSClients.get_dynamodb_resource()


def get_sns() -> boto3.client:
    """Convenience function to get SNS client"""
    return AWSClients.get_sns_client()


def get_sns_client() -> boto3.client:
    """Convenience function to get SNS client (alias for compatibility)"""
    return AWSClients.get_sns_client()


def get_bedrock() -> boto3.client:
    """Convenience function to get Bedrock client"""
    return AWSClients.get_bedrock_client()


def get_bedrock_client() -> boto3.client:
    """Convenience function to get Bedrock client (alias for compatibility)"""
    return AWSClients.get_bedrock_client()


def get_lambda() -> boto3.client:
    """Convenience function to get Lambda client"""
    return AWSClients.get_lambda_client()


def get_lambda_client() -> boto3.client:
    """Convenience function to get Lambda client (alias for compatibility)"""
    return AWSClients.get_lambda_client()


def get_events_client() -> boto3.client:
    """Convenience function to get EventBridge client (alias for compatibility)"""
    return AWSClients.get_events_client()


def get_apigateway_management_client() -> boto3.client:
    """Convenience function to get API Gateway Management client (alias for compatibility)"""
    return AWSClients.get_apigateway_client()
