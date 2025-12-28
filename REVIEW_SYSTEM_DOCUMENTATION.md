# Review System Documentation

## Overview
This document describes how the review and customer tracking system worked before removal.

## Review Command (`/review`)

**Location:** `commands/review.py`

**Command Structure:**
- `/review user:<trainer_mention> gamemode:<gamemode> rating:<1-5> review:<text>`

**Parameters:**
- `user`: Discord user mention of the trainer being reviewed
- `gamemode`: Gamemode string (autocomplete with emoji)
- `rating`: Integer 1-5 (autocomplete shows 1-5)
- `review`: Review text

**Validation:**
1. Rating must be between 1 and 5
2. User must be a customer of the trainer (checked via `database.is_customer()`)

**Functionality:**
1. Ensures trainer exists in database (`database.add_trainer()`)
2. Gets trainer IGN using `database.get_trainer_ign()`
3. Creates star emoji string: `"⭐" * rating`
4. Finds review channel from config (`config.review_channel = "reviews"`)
5. Stores review in database using `database.add_review()`
6. Sends embed to review channel with:
   - Title: `"New {gamemode} review of {trainer_ign}!"`
   - Description: stars + review text
   - Thumbnail: `https://render.crafty.gg/3d/bust/{trainer_ign}`
   - Author: reviewer's display name and avatar
7. Responds with "Review submitted." (ephemeral)

**Autocomplete:**
- Gamemode: Shows `"{emoji} {name}"` format (e.g., "⚔️ Sword")
- Rating: Shows "1", "2", "3", "4", "5"

## Customer Tracking System

### Database Structure
**Column:** `customers` in `trainers` table
- Type: TEXT (stores JSON array)
- Default: `"[]"` (empty JSON array)
- Stores: Array of customer Discord user IDs as integers

**Example data:**
```json
"[123456789, 987654321]"
```

### Database Functions

**`add_customer_to_trainer(gamemode, trainer_id, customer_id)`**
- Ensures trainer entry exists (`add_trainer()`)
- Retrieves current customers list from database
- Parses JSON array
- Adds customer_id if not already present
- Updates database with new JSON array

**`is_customer(gamemode, trainer_id, customer_id)`**
- Queries customers column for trainer
- Returns `False` if trainer entry doesn't exist or customers is NULL/empty
- Parses JSON array
- Returns `True` if customer_id is in the array, `False` otherwise

### Usage in `/close` Command
When a trainer closes a ticket using `/close`:
1. Gets ticket info (gamemode, trainer_id, customer_id)
2. Calls `database.add_customer_to_trainer()` to add customer to trainer's list
3. This ensures only customers who completed training can leave reviews

## Database Review Operations

**Table:** `reviews`
```sql
CREATE TABLE IF NOT EXISTS reviews (
    trainer_id INTEGER,
    gamemode TEXT,
    reviewer_id INTEGER,
    rating INTEGER,
    review_text TEXT,
    PRIMARY KEY (trainer_id, gamemode, reviewer_id)
)
```

**Function:** `add_review(trainer_id, gamemode, reviewer_id, rating, review_text)`
- Uses `INSERT OR REPLACE` (allows updating existing reviews)
- Primary key ensures one review per trainer/gamemode/reviewer combination

## Config Settings

**`config.py`:**
```python
review_channel = "reviews"
```
- Used to find the channel where review embeds are sent
- Searches guild channels by name (case-insensitive)

## Integration Points

1. **Bot Setup:** `bot.py` automatically loads `commands/review.py` via dynamic module loading
2. **Close Command:** Adds customers when tickets are closed
3. **Review Command:** Validates customer status before allowing review

