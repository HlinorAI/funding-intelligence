# History

`applications.yaml` — append-only log of real applications, outcomes and lessons.

Do not overwrite a previous result. If a route is retried, add a new record with a new date and link it to the previous record using `retry_of`.

The runner does not write history automatically in v1. A human or later feedback-loop command should append only confirmed outcomes.
