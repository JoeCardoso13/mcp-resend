---
name: mcp-resend-service
description: Provides knowledge of how to use MCP Resend most effectively. It's loaded into the agent's context when running the MCP.
---

# Resend MCP Server — Skill Guide

## Tools

| Tool | Use when... |
|------|-------------|
| `send_email` | You need to send an email to one or more recipients |
| `get_email` | You have an email ID and need delivery status or details |
| `list_emails` | You need to browse sent emails |
| `create_contact` | You need to add a new contact |
| `get_contact` | You have a contact ID and need their details |
| `list_contacts` | You need to browse contacts, optionally filtered by segment |
| `update_contact` | You need to change a contact's name or subscription status |
| `delete_contact` | You need to remove a contact |
| `list_segments` | You need to see available contact segments |

## Context Reuse

- Use the `id` from `list_emails` results when calling `get_email`
- Use the `id` from `list_contacts` results when calling `get_contact`, `update_contact`, or `delete_contact`
- Use the `id` from `list_segments` when filtering `list_contacts` by `segment_id`

## Workflows

### 1. Send and Track
1. `send_email` to send the message
2. `get_email` with the returned ID to check delivery status (`last_event`)

### 2. Audience Sync
1. `list_segments` to find the target segment
2. `list_contacts` with `segment_id` to see current members
3. `create_contact` to add new contacts
4. `update_contact` to fix names or change subscription status
5. `delete_contact` to remove bounced or invalid addresses
