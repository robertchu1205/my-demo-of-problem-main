# Interview challenge

## emphasis about my project

`clarifying from back forward`

- CI
   - For private and convenience, I just clarified how I would like to versioned the tag of docker images. Now I only defined .github.sha on the tag of docker image. It's definitely better if we only build and pack when it's a tag push. So we can just use ${{ github.ref }} on the tag of docker image and alter the version in Chart.yaml by bash command 'sed'
   - In pytest, I only test 'GET' api for answering faster. And it will assert 400 when GET the endpoint, '/v1/history' because I doesn't make the redis server up during the pytest.
- Database
   - I picked redis server because it answers the fastest and is easiest for developers to use. I start writing and reading right after redis server's up
- Helm Chart
   - I only simply expose the service by ClusterIP since I assume the project's only in development phase and tested in internal network

## Coding Challenge

Please create a REST API based on the attached OpenAPI/Swagger definition in your preferred language (Node.JS, TypeScript, Go, Python, Ruby, Perl, Crystal, Nim, etc.). In addition to the endpoints included in the Swagger definition, please ensure that a Prometheus metrics endpoint is available in your application under `/metrics`. The application should also provide a `/health` endpoint.

The `/` (root) endpoint should provide the current date (UNIX epoch) and version. Additionally, a boolean property called Kubernetes should indicate if the application is running under Kubernetes. Below is an example of the expected output.

```json
{
   "version": "0.1.0",
   "date": 1663534325,
   "kubernetes": false
}
```

The `/v1/tools/lookup` endpoint should resolve ONLY the IPv4 addresses for the given domain. Make sure you log all successful queries and their result in a database of your choosing (PostgreSQL, MySQL/MariaDB, MongoDB, Redis, ElasticSearch, SurrealDB, etc.). No SQLite or file-based databases, as we're planning on deploying this service to Kubernetes.

For the `/v1/tools/validate` endpoint, the service should validate if the input is an IPv4 address or not.

The `/v1/history` endpoint should retrieve the latest 20 saved queries from the database and display them in order (the most recent should be first).

Please ensure the service starts on port 3000 and your REST API has an access log. Uh-oh, don't forget about graceful shutdowns.

If possible, please make sure the OpenAPI/Swagger is available so we can generate a client for your service (not mandatory).
`/api/docs`

## Development environment

Create a fully Dockerized development environment using Docker and Docker Compose. Also, ensure all services and tools are included in the Docker Compose definition and that everything starts in the correct order and initializes correctly (migrations, etc.). We should be able to run everything with a simple:

```
docker-compose up -d --build
```

The Dockerfile and Docker Compose files should be available in the root directory of your project.

## Tasks for DevOps roles only
**For candidates applying for our Back-end/full-stack roles, this part is optional.**

### Kubernetes support

We plan on running your application in Kubernetes, so please provide either Kubernetes manifests or a Helm Chart. We prefer Helm Charts. Also, please store sensitive data in Kubernetes secrets (database passwords, etc.)

`helm install my-demo .`

### CI Pipeline

Add a CI pipeline (GitHub Actions, GitLab CI, etc.) to test (basic tests, linting, etc.), build (Docker only), and package (Helm chart) your application upon each commit. The artifact of your build should be at least a versioned Docker image.

## References
- https://12factor.net/
- https://swagger.io/
- https://docs.docker.com/compose/
- https://minikube.sigs.k8s.io/docs/
- https://helm.sh/

---

**Notes:**

- We appreciate simple, clean, idiomatic code and essential documentation.
- Any improvements on the Swagger/OpenAPI definitions are welcome.
- Pay attention to details.
