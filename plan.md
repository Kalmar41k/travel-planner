# Python engineer test assessment - Travel Planner

### Overview

This task involves building a CRUD application. The goal is to create a system that showcases your understanding in building RESTful APIs, interacting with databases, and integrating third-party services. The test assessment is expected to be done within 2 hours.

### Requirements

Travel Company asked you to create a management application that helps travellers plan trips and collect desired places to visit. They need a system to manage travel projects, places retrieved from a public API, and notes that users attach to places.

From the user’s perspective, a project consists of a collection of places they want to visit. One project can contain multiple places (minimum: 1, maximum: 10). While planning, travellers should be able to add notes to a specific place, update those notes over time, and eventually mark the place as visited. When all places in a project are marked as visited, the project is marked as completed.

### **Backend Requirements:**

- **Travel Projects**
    - Ability to create a travel project in the system
        - A project is described as Name, Description (optional), Start Date (optional)
    - Ability to remove travel projects from the system
        - A project **cannot** be deleted if **any** of its places are already marked as visited
    - Ability to update travel project information (Name, Description, Start Date)
    - Ability to list travel projects
    - Ability to get a single travel project
- **Places / Project Places**
    - Ability to create a project **with places** in one single request
        - A project creation request may include an array of places imported from a third-party API
        - Each place is identified by an external ID from the API
    - Ability to add a place to an existing project
        - The backend must validate that the place exists in the third-party API before storing it
    - Ability to update a place within a project
        - Ability to update `notes`
        - Ability to mark a place in project as `visited`
    - Ability to list all places for a project
    - Ability to get a single place within a project
- **General**
    - Framework
        - Use any of: **FastAPI**, **Django, Flask**
    - Database
        - You can use any database (SQLite is sufficient)
    - Third-party API
        - Use the **Art Institute of Chicago API** to fetch and validate places
        - API documentation: https://api.artic.edu/docs/#collections
        - Example endpoint:
            - `GET https://api.artic.edu/api/v1/artworks/search`
    - Validations
        - Make sure endpoints validate the request body and return appropriate HTTP status codes
        - Validate that a place exists in the Art Institute API before adding it to a project
        - Enforce limits (maximum 10 places per project)
        - Prevent adding the same external place to the same project more than once

### **Bonus Points**

Additional points will be given for implementing any of the following:

- **Docker**
    - Dockerfile and/or docker-compose configuration for running the application locally
- **Postman Collection**
    - A complete Postman collection covering all endpoints and common use cases
- **Extended Business Logic**
    - Pagination and filtering for listing endpoints
    - Caching responses from the third-party API
    - Basic authentication
- **Code Quality**
    - Clear project structure
    - Meaningful commit history

### Sharing the results

- Make a repository on **GitHub**
- Add a **README** explaining how to build and start the application. Include any information you think will be useful (setup steps, environment variables, example requests)
- Define all of the endpoints in a **Postman collection** (or provide OpenAPI/Swagger documentation) and add a link to it in the README
- Once the repository is ready, share a link to it with our recruiter. We will review it within 5–7 business days and return with feedback
- Don't hesitate to ask any questions

Thank you!