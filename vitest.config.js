import { defineConfig } from "vitest/config";

export default defineConfig({
    test: {
        environment: "jsdom",
        include: ["tests/js/**/*.test.js"],
        coverage: {
            provider: "v8",
            reporter: [["text", { skipFull: true }]],
            include: [
                "src/django_admin_radio_select/static/django_admin_radio_select/**/*.js",
            ],
        },
    },
});
