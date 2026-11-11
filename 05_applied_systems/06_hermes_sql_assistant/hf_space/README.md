---
title: Enterprise SQL Assistant
emoji: 🗄️
colorFrom: green
colorTo: blue
sdk: static
pinned: false
---

# 🗄️ Enterprise SQL Assistant

Ask questions about a sample company database in plain English — the app maps them to **read-only** SQL and returns the results.

## How it works

Everything runs **in your browser**: the SQLite database is embedded in the page and executed through [sql.js](https://sql.js.org) (SQLite compiled to WebAssembly). No server, no GPU, no API key — which is why this runs on the Hugging Face **free static tier**.

## Try these

- "Show all customers"
- "What is the total sales?"
- "Sales by customer name"
- "Orders placed in October 2026"
- "Customers from Egypt"

## Schema

| table | columns |
|---|---|
| `customers` | `customer_id`, `name`, `country` |
| `orders` | `order_id`, `customer_id`, `amount`, `order_date` |

## Safety

Only `SELECT` statements are ever executed. Any query containing `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `PRAGMA`, `ATTACH`, etc. is rejected before it reaches SQLite.
