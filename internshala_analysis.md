# Internshala Website Analysis

## Overview
- Base URL: `http://internshala.com/internships`
- Detail Page Example: `https://internshala.com/internship/detail/12345`

## HTML Elements
### Listing Page
- Internship Card: `<div class="internship_meta">`
- Job Title: `<h3 class="heading_4_5">` or similar
- Company: `<a class="link_display_like_text">`
- Location: `<span class="location">`
- Stipend: `<span class="stipend">`

### Detail Page
- Job Title: `<h1 class="heading_title">`
- Company: `<a class="link_display_like_text">` or `<div class="company">`
- Location: `<span class="location">` or `<div class="location_container">`
- Stipend: `<span class="stipend">` or `<div class="stipend_container">`
- Duration: `<div class="item_body">` under "Duration"
- Apply By: `<div class="item_body">` under "Apply By"
- Description: `<div class="internship_details">`

## Pagination Patterns
- URL: `/page-2` (increments with each page)
- Element: `<ul class="pagination">` with `<li><a href="/page-2">2</a></li>`

## Dynamic Content Loading
- Method: JavaScript/AJAX (e.g., `api/internships?start=20`)
- Trigger: Scroll event loading more cards