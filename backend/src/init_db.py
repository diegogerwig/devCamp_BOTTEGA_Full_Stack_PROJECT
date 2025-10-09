def init_database(app, db):
    if not db:
        print("⚠️ No database, using mock data")
        return
    
    try:
        with app.app_context():
            print("🔄 Checking database structure...")
            try:
                # Check if 'users_password' column exists
                result = db.session.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'users_password'
                """))
                has_users_password = result.fetchone() is not None
                
                if not has_users_password:
                    print("⚠️  Column 'users_password' does not exist, checking alternatives...")
                    
                    # Check if old 'password' column exists
                    result = db.session.execute(db.text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' 
                        AND column_name = 'password'
                    """))
                    has_password = result.fetchone() is not None
                    
                    if has_password:
                        print("✅ Renaming 'password' to 'users_password'...")
                        db.session.execute(db.text("ALTER TABLE users RENAME COLUMN password TO users_password"))
                        db.session.commit()
                        print("✅ Migration completed!")
                    else:
                        print("⚠️  Creating column 'users_password'...")
                        db.session.execute(db.text("ALTER TABLE users ADD COLUMN users_password VARCHAR(255)"))
                        db.session.commit()
                        print("✅ Column created!")
                else:
                    print("✅ Column 'users_password' exists correctly")
                    
            except Exception as e:
                print(f"⚠️ Error in automatic migration: {e}")
                
            # Get database type from app config or global variable
            database_type = getattr(app, 'DATABASE_TYPE', 'PostgreSQL')
            print(f"✅ Using existing {database_type} tables")
                
    except Exception as e:
        print(f"⚠️ Database init info: {e}")