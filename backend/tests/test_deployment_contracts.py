"""Source-level guards for image contents and the Cloud Run port contract."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class DeploymentContractTests(unittest.TestCase):
    def test_cloud_run_api_image_uses_port_and_production_safe_defaults(self):
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("PORT=8080", dockerfile)
        self.assertIn("ENVIRONMENT=production", dockerfile)
        self.assertIn("SEED_DEMO_DATA=false", dockerfile)
        self.assertIn("requirements-production.txt", dockerfile)
        self.assertIn("MAX_FILE_SIZE=25165824", dockerfile)
        self.assertIn("USER homzdoctor", dockerfile)

    def test_demo_seeds_patient_uploads_and_tests_are_excluded_from_images(self):
        root_ignore = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
        backend_ignore = (ROOT / "backend" / ".dockerignore").read_text(encoding="utf-8").splitlines()
        for pattern in ("backend/core/seed.py", "**/uploads/", "**/tests/", "**/*.db"):
            self.assertIn(pattern, root_ignore)
        for pattern in ("uploads/", "tests/", "*.db"):
            self.assertIn(pattern, backend_ignore)
        # The Cloud Run root context omits the demo-seed module entirely. The backend-context
        # image keeps it available only for an explicitly isolated local Compose demo; both
        # Dockerfile settings default to production with seeding disabled.
        self.assertTrue((ROOT / "backend" / "core" / "seed.py").is_file())
        backend_docker = (ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("ENVIRONMENT=production", backend_docker)
        self.assertIn("SEED_DEMO_DATA=false", backend_docker)
        self.assertNotIn("core/seed.py", backend_ignore)

    def test_backend_images_install_asyncpg_for_postgresql_and_use_runtime_port(self):
        dockerfile = (ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("requirements-production.txt", dockerfile)
        self.assertIn("${PORT:-8000}", dockerfile)

    def test_cloud_build_frontend_uses_its_own_build_context(self):
        cloudbuild = (ROOT / "cloudbuild-frontend.yaml").read_text(encoding="utf-8")
        self.assertIn("dir: frontend", cloudbuild)
        self.assertIn("- Dockerfile", cloudbuild)
        guide = (ROOT / "GOOGLE_CLOUD_DEPLOYMENT.md").read_text(encoding="utf-8")
        self.assertIn("--config=cloudbuild-frontend.yaml .", guide)

    def test_vercel_services_have_port_aware_container_entrypoints(self):
        import json

        config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
        self.assertEqual(config["services"]["backend"]["root"], "backend/")
        self.assertEqual(config["services"]["frontend"]["root"], "frontend/")
        self.assertEqual(config["services"]["backend"]["entrypoint"], "Dockerfile.vercel")
        self.assertEqual(config["services"]["frontend"]["entrypoint"], "Dockerfile.vercel")
        self.assertTrue(any(rule.get("destination", {}).get("service") == "backend" for rule in config["rewrites"]))
        self.assertTrue(
            any(rule.get("source") == "/ws" and rule.get("destination", {}).get("service") == "backend"
                for rule in config["rewrites"]),
            "the exact /ws path must route to the API service",
        )
        self.assertTrue(
            any(rule.get("source") == "/ws/(.*)" and rule.get("destination", {}).get("service") == "backend"
                for rule in config["rewrites"]),
            "WebSocket subpaths must route to the API service",
        )
        backend = (ROOT / "backend" / "Dockerfile.vercel").read_text(encoding="utf-8")
        frontend = (ROOT / "frontend" / "Dockerfile.vercel").read_text(encoding="utf-8")
        self.assertRegex(backend, r"(?m)^[ \t]+PORT=8080[ \t]*\\$")
        self.assertIn("${PORT:-8080}", backend)
        self.assertRegex(frontend, r"(?m)^ENV PORT=8080[ \t]*\\$")
        self.assertIn("listen ${PORT};", (ROOT / "frontend" / "nginx.conf.template").read_text(encoding="utf-8"))

    def test_full_stack_compose_uses_required_secrets_and_persistent_volumes(self):
        compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        for value in ("postgres:", "api:", "web:", "qdrant:", "redis:"):
            self.assertIn(value, compose)
        self.assertIn("${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD", compose)
        self.assertIn("${SECRET_KEY:?Set SECRET_KEY", compose)
        self.assertIn("homzdoctor_uploads:/app/uploads", compose)
        self.assertIn("postgres_data:", compose)

    def test_frontend_nginx_honors_port_and_proxies_https_backend(self):
        dockerfile = (ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")
        config = (ROOT / "frontend" / "nginx.conf.template").read_text(encoding="utf-8")
        self.assertIn("PORT=8080", dockerfile)
        self.assertIn("listen ${PORT};", config)
        self.assertIn("proxy_pass ${BACKEND_SCHEME}://$backend_upstream;", config)
        self.assertGreaterEqual(config.count("proxy_ssl_verify on;"), 2)
        self.assertIn("client_max_body_size ${MAX_REQUEST_BODY_SIZE};", config)


if __name__ == "__main__":
    unittest.main()
