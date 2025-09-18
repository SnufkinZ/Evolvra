{
  "_id": "unique_task_id",
  "user_id": "owner_user_id",
  "name": "Memory Words",
  "target_goal_ids": [
    "goal_id_english",
    "goal_id_vocabulary",
    "goal_id_listening"
  ],
  "target_goal_names": [
    "English Improvement",
    "Vocabulary Expansion",
    "Listening Skills"
  ],
  "status": "active", // active | completed | paused | cancelled

  "dynamic_priority": {
    "value": 75,
    "value_factors": {
      "urgency": 30,
      "importance": 25,
      "due_soon": 20,
      "user_defined": 5,
      "contextual_relevance": 10,
      "historical_performance": 5
    },
    "value_to_goal": 80,
    "confidence": 95,
    "last_updated": "2025-08-09T10:15:00Z",
    "source": "Me"
  },

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
  ]

  "metrics": {
    "success_count": 12,
    "failure_count": 3,
    "created_at": "2025-07-01T09:00:00Z",
    "last_done_at": "2025-08-09T22:00:00Z"
  },

  "tags": ["english", "anki", "study"]
}
