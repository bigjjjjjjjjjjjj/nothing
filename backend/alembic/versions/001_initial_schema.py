"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-11-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 建立courses表
    op.create_table(
        'courses',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('user_id', sa.String(50), nullable=False, index=True),
        sa.Column('meeting_id', sa.String(100), unique=True, index=True),
        sa.Column('meeting_url', sa.String(255)),
        sa.Column('course_name', sa.String(255)),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # 建立slides表
    op.create_table(
        'slides',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('course_id', sa.String(50), nullable=False, index=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('total_pages', sa.Integer()),
        sa.Column('extracted_text', sa.Text()),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )

    # 建立transcripts表
    op.create_table(
        'transcripts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('course_id', sa.String(50), nullable=False, index=True),
        sa.Column('timestamp', sa.String(20), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )

    # 建立course_summaries表
    op.create_table(
        'course_summaries',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('course_id', sa.String(50), unique=True, nullable=False),
        sa.Column('summary_json', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )

    # 建立quizzes表
    op.create_table(
        'quizzes',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('course_id', sa.String(50), nullable=False, index=True),
        sa.Column('scope_id', sa.String(50)),
        sa.Column('questions_json', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )

    # 建立quiz_submissions表
    op.create_table(
        'quiz_submissions',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('quiz_id', sa.String(50), nullable=False, index=True),
        sa.Column('user_id', sa.String(50), nullable=False, index=True),
        sa.Column('answers_json', postgresql.JSONB(), nullable=False),
        sa.Column('results_json', postgresql.JSONB()),
        sa.Column('score', sa.Integer()),
        sa.Column('submitted_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
    )

    # 建立teacher_hints表
    op.create_table(
        'teacher_hints',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('course_id', sa.String(50), nullable=False, index=True),
        sa.Column('timestamp', sa.String(20), nullable=False),
        sa.Column('hint_text', sa.Text(), nullable=False),
        sa.Column('hint_type', sa.String(20), nullable=False),
        sa.Column('related_concept', sa.String(255)),
        sa.Column('slide_page', sa.Integer()),
        sa.Column('confidence', sa.Float()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )

    # 建立複合索引
    op.create_index(
        'idx_teacher_hints_course_type',
        'teacher_hints',
        ['course_id', 'hint_type']
    )

    # 建立user_stats表
    op.create_table(
        'user_stats',
        sa.Column('user_id', sa.String(50), primary_key=True),
        sa.Column('total_courses', sa.Integer(), server_default='0'),
        sa.Column('total_quizzes_taken', sa.Integer(), server_default='0'),
        sa.Column('average_score', sa.Float(), server_default='0.0'),
        sa.Column('weak_concepts', postgresql.JSONB()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('user_stats')
    op.drop_index('idx_teacher_hints_course_type', 'teacher_hints')
    op.drop_table('teacher_hints')
    op.drop_table('quiz_submissions')
    op.drop_table('quizzes')
    op.drop_table('course_summaries')
    op.drop_table('transcripts')
    op.drop_table('slides')
    op.drop_table('courses')
