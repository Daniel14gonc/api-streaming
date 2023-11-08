# Netflix-like web app

For this project, we built a web application, resembling Netflix. We made an API on Flask, connected
to a PostgreSQL database on AWS.

## Features 🚀

- Account creation: You were able to create your own account on the app. There were three different
  tiers of subscription, which were just dummy in economic terms but each tier had its own
  characteristics. The lower tier included ads and you could only create one profile. The middle
  tier, included less ads and you could create two profiles. The upper tier eliminated ads and
  you could create up to four profiles.
- Recommendations: Based on the content you consumed, the application recommended movies related.
  It was a basic recommendation system, using joins on the database.
- Reports: For administrators, there was an interface in which they could access information
  regarding transactions on the system. It included most viewed movies, most active users,
  accounts created recently, etc. We used triggers and stored procedures for some.

You can also view the [UI repo](https://github.com/Manuel-Archila/Streaming_UI.git).
