// Commitlint configuration
// See: https://commitlint.js.org/
// Follows Conventional Commits: https://www.conventionalcommits.org/

module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    // Type must be one of the following
    "type-enum": [
      2,
      "always",
      [
        "feat", // New feature
        "fix", // Bug fix
        "docs", // Documentation only changes
        "style", // Changes that do not affect the meaning of the code
        "refactor", // Code change that neither fixes a bug nor adds a feature
        "perf", // Performance improvement
        "test", // Adding missing tests or correcting existing tests
        "build", // Changes that affect the build system or external dependencies
        "ci", // Changes to CI configuration files and scripts
        "chore", // Other changes that don't modify src or test files
        "revert", // Reverts a previous commit
        "wip", // Work in progress
      ],
    ],
    // Type must be lowercase
    "type-case": [2, "always", "lower-case"],
    // Subject must not be empty
    "subject-empty": [2, "never"],
    // Subject must not end with a period
    "subject-full-stop": [2, "never", "."],
    // Subject must start with lowercase or be an acronym (optional)
    // Uncomment below if you want to allow acronyms like API, UI, CSS
    // "subject-case": [1, "always", ["lower-case", "start-case"]],
    // Header max length (type + scope + subject)
    "header-max-length": [2, "always", 100],
    // Body max line length
    "body-max-line-length": [1, "always", 100],
    // Footer max line length
    "footer-max-line-length": [1, "always", 100],
  },
  // Custom help message
  helpUrl:
    "https://github.com/conventional-changelog/commitlint/#what-is-commitlint",
};
