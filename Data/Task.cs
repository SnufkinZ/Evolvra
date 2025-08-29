{
  "_id": { "$oid": "68968a4a1ae8ab54502b8196" },

  "name": "Memory Words",
  "target_goal": "English::Vocabulary",
  "weight": 85,
  "status": "active",

  "frequency": {
    "field": "DAILY", // DAILY | WEEKLY | MONTHLY | YEARLY | QUANTITY
    "times": 1, //  If frequency is WEEKLY, this is once a week. If frequency is QUANTITY, this is the number of times to repeat.
    "source": "owner",
    "confidence": 99,
    "last_updated": "2025-08-09T10:15:00Z"
  },

  "description": {
    "field": "I wants to use AnkiDroid to do this task.",
    "source": "owner",
    "confidence": 99,
    "last_updated": "2025-08-09T10:15:00Z"
  },

  "preschedule": [
    {
      "mode": "absolute",
      "start": "2025-08-10T14:00:00Z",
      "end": "2025-08-10T14:30:00Z",
      "location": "Home",
      "source": "owner",
      "confidence": 99
    },
    {
      "mode": "fuzzy",
      "nl_start": "after lunch",
      "window": { "start": "2025-08-10T13:00:00Z", "end": "2025-08-10T15:00:00Z" },
      "location": "Restaurant",
      "source": "owner",
      "confidence": 90,
      "resolved": false
    },
    {
      "mode": "fuzzy",
      "nl_start": "today",
      "window": { "start": "2025-08-10T08:00:00Z", "end": "2025-08-10T22:00:00Z" },
      "todo_list": [ "Write definition for each word" ],
      "source": "owner",
      "confidence": 99,
      "resolved": false
    },
    {
      "mode": "workflow",
      "nl_start": "next implement",
      "window": { "start": "none", "end": "none" },
      "location": none,
      "source": "owner",
      "confidence": 99,
      "content": "Memory the next unit of words, and at the same time review the previous unit of words.",
    },
    {
      "mode": "workflow",
      "nl_start": "next implement",
      "window": { "start": "none", "end": "none" },
      "location": none,
      "source": "owner",
      "confidence": 99,
      "content": "dictate the words I have learned before.",
    }
  ],

  "srs_memory": {
    "enabled": true,
    "system": "SM2",
    "deck": "English::Vocabulary",
    "next_review_at": "2025-08-10T18:00:00Z",
    "last_review_at": "2025-08-09T18:00:00Z",
    "ease": 2.5,
    "interval_days": 3
  },

  "metrics": {
    "success_count": 12,
    "failure_count": 3,
    "last_verified_at": "2025-08-09T22:00:00Z"
  },

  "tags": ["english", "anki", "study"]
}
