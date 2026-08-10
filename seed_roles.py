import psycopg2

DATABASE_URL = "postgresql://wildlife_database_user:G9KvbZGfrexZROT9gIQ4VtHG0iMCyNs2@dpg-d9os19ugekts73en9rm0-a.ohio-postgres.render.com/wildlife_database"

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute("""
        INSERT INTO roles (name, description) VALUES
            ('admin', 'Full platform administration'),
            ('researcher', 'Wildlife Researcher'),
            ('conservation_officer', 'Conservation Officer'),
            ('forest_department', 'Forest Department Officer')
        ON CONFLICT (name) DO NOTHING;
    """)

print("Roles seeded.")
conn.close()