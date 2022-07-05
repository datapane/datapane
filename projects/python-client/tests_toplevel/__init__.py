"""
Tests in top-level are special in that they are executing individually.
This is so we can test global functions, such as config file generation, without breaking/invalidating any other tests, affecting mutable state,
or being influenced by default behaviour (i.e. mocks can run prior to importing the library)
"""
