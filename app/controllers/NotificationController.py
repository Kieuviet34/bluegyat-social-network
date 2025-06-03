from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import text
from app.extensions import db
from app.models.notification import Notification
from app.models.user import friendships
from datetime import datetime, timezone

notification_bp = Blueprint(
    'notification'
)
