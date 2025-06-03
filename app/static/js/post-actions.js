if (!window.PostActions) {
const PostActions = {
    initialized: false,

    initialize() {
        if (this.initialized) return;

        // Use event delegation for like and comment actions
        document.body.addEventListener('submit', (e) => {
            if (e.target.matches('.like-form')) {
                this.handleLikeSubmit(e);
            } else if (e.target.matches('#commentForm')) {
                this.handleCommentSubmit(e);
            }
        });

        document.body.addEventListener('click', (e) => {
            if (e.target.closest('.comment-btn')) {
                this.handleCommentClick(e);
            }
            // Edit Post
            const editBtn = e.target.closest('.edit-post-btn');
            if (editBtn) {
                this.handleEditPostClick(editBtn);
            }
            // Delete Post
            const deleteBtn = e.target.closest('.delete-post-btn');
            if (deleteBtn) {
                this.handleDeletePostClick(deleteBtn);
            }
        });

        // Edit Post Form submit
        const editPostForm = document.getElementById('editPostForm');
        if (editPostForm) {
            editPostForm.addEventListener('submit', this.handleEditPostSubmit.bind(this));
        }

        this.initialized = true;
        console.log('PostActions initialized');
    },

    async handleLikeSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const icon = form.querySelector('.fa-heart');
        if (!icon) return;
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            });
            const data = await response.json();
            const count = form.querySelector('.like-count');
            if (data.liked) {
                icon.classList.add('text-danger');
            } else {
                icon.classList.remove('text-danger');
            }
            if (count) count.textContent = data.count;
            icon.style.transform = 'scale(1.3)';
            setTimeout(() => icon.style.transform = 'scale(1)', 200);
        } catch (error) {
            console.error('Error liking post:', error);
            icon.style.transform = 'translateX(3px)';
            setTimeout(() => icon.style.transform = 'translateX(-3px)', 100);
            setTimeout(() => icon.style.transform = 'translateX(0)', 200);
        }
    },

    async handleCommentSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const postId = form.dataset.postId;
        const contentInput = form.content;
        if (!contentInput) {
            this.showFormError(form, 'Comment input not found');
            return;
        }
        const content = contentInput.value.trim();
        if (!content) {
            this.showFormError(form, 'Comment cannot be empty');
            return;
        }
        this.showSubmitting(form, true);
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        if (!csrfToken) {
            this.showFormError(form, 'CSRF token not found');
            this.showSubmitting(form, false);
            return;
        }
        try {
            const response = await fetch(`/posts/${postId}/comments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ content })
            });
            const data = await response.json();

            if (data.success) {
                contentInput.value = '';
                this.hideFormError(form);
                this.loadComments(postId);
                this.updateCommentCount(postId, 1);
            } else {
                this.showFormError(form, data.error || 'Failed to add comment');
            }
        } catch (error) {
            console.error('Error adding comment:', error);
            this.showFormError(form, 'Failed to add comment. Please try again.');
        } finally {
            this.showSubmitting(form, false);
        }
    },

    handleCommentClick(e) {
        const btn = e.target.closest('.comment-btn');
        if (!btn) return;

        const postId = btn.dataset.postId;
        if (postId) this.loadPostDetail(postId);
    },

    loadPostDetail(postId) {
        const modal = document.getElementById('postDetailModal');
        if (!modal) return;
        modal.dataset.postId = postId;
        const postContent = modal.querySelector('.post-content');
        if (postContent) postContent.innerHTML = '<div class="text-center"><div class="spinner-border"></div></div>';
        const commentForm = document.getElementById('commentForm');
        if (commentForm) commentForm.dataset.postId = postId;
        new bootstrap.Modal(modal).show();
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        if (!csrfToken) return;
        fetch(`/posts/${postId}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (postContent) postContent.innerHTML = data.content;
            this.loadComments(postId);
        })
        .catch(() => {
            if (postContent) postContent.innerHTML = '<div class="alert alert-danger">Failed to load post</div>';
        });
    },

    loadComments(postId) {
        const commentsList = document.querySelector('.comments-list');
        commentsList.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-primary"></div></div>';

        fetch(`/posts/${postId}/comments`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            }
        })
        .then(response => response.json())
        .then(comments => {
            if (comments.length === 0) {
                commentsList.innerHTML = '<p class="text-muted text-center">No comments yet</p>';
                return;
            }

            commentsList.innerHTML = comments.map(comment => `
                <div class="comment-item d-flex align-items-start mb-3" data-comment-id="${comment.id}">
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center">
                            <strong class="me-2">${comment.author}</strong>
                            <small class="text-muted">${comment.created_at}</small>
                        </div>
                        <p class="mb-0">${comment.content}</p>
                    </div>
                    ${comment.can_modify ? `
                        <button class="btn btn-link text-muted p-0 ms-2 comment-actions" 
                                onclick="showCommentActions(${comment.id})">
                            <i class="fas fa-ellipsis-h"></i>
                        </button>
                    ` : ''}
                </div>
            `).join('');
        })
        .catch(() => {
            commentsList.innerHTML = '<div class="alert alert-danger">Failed to load comments</div>';
        });
    },

    showFormError(form, message) {
        const feedback = form.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.textContent = message;
            feedback.style.display = 'block';
        }
        form.classList.add('was-validated');
    },

    hideFormError(form) {
        form.classList.remove('was-validated');
        const feedback = form.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.style.display = 'none';
        }
    },

    showSubmitting(form, isSubmitting) {
        const spinner = form.querySelector('.spinner-border');
        const submitBtn = form.querySelector('button[type="submit"]');
        if (spinner && submitBtn) {
            spinner.classList.toggle('d-none', !isSubmitting);
            submitBtn.disabled = isSubmitting;
        }
    },

    updateCommentCount(postId, delta) {
        const postCard = document.querySelector(`[data-post-id="${postId}"]`);
        const commentCount = postCard?.querySelector('.comment-count');
        if (commentCount) {
            commentCount.textContent = Math.max(0, parseInt(commentCount.textContent) + delta);
        }
    },

    handleEditPostClick(btn) {
        const postId = btn.dataset.postId;
        const content = btn.dataset.postContent;
        // Get media_url from the post card's <img> if present
        let mediaUrl = '';
        const postCard = document.getElementById(`post-${postId}`);
        if (postCard) {
            const img = postCard.querySelector('img');
            if (img) mediaUrl = img.getAttribute('src');
        }
        const modal = document.getElementById('editPostModal');
        if (!modal) return;
        document.getElementById('editPostId').value = postId;
        document.getElementById('editPostContent').value = content;
        new bootstrap.Modal(modal).show();
    },

    async handleEditPostSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const postId = document.getElementById('editPostId').value;
        const content = document.getElementById('editPostContent').value.trim();
        const media_url = document.getElementById('editPostMediaUrl').value.trim();
        const feedback = form.querySelector('.invalid-feedback');
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        if (!content) {
            feedback.textContent = 'Content cannot be empty';
            feedback.style.display = 'block';
            return;
        }
        feedback.style.display = 'none';
        try {
            const response = await fetch(`/posts/${postId}/edit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ content, media_url })
            });
            if (response.ok) {
                // Update content
                document.getElementById(`post-content-${postId}`).textContent = content;
                // Update media image
                const postCard = document.getElementById(`post-${postId}`);
                if (postCard) {
                    let img = postCard.querySelector('img');
                    if (media_url) {
                        if (!img) {
                            img = document.createElement('img');
                            img.className = 'img-fluid rounded mb-2';
                            img.alt = 'Post media';
                            postCard.querySelector('.card-body').insertBefore(img, postCard.querySelector('.d-flex.align-items-center.mt-3'));
                        }
                        img.src = media_url;
                        img.style.display = '';
                    } else if (img) {
                        img.style.display = 'none';
                    }
                }
                bootstrap.Modal.getInstance(document.getElementById('editPostModal')).hide();
            } else {
                feedback.textContent = 'Failed to update post';
                feedback.style.display = 'block';
            }
        } catch (err) {
            feedback.textContent = 'Error updating post';
            feedback.style.display = 'block';
        }
    },

    handleDeletePostClick(btn) {
        const postId = btn.dataset.postId;
        if (!postId) return;
        if (confirm('Are you sure you want to delete this post?')) {
            // Gửi request xóa post (bạn có thể hoàn thiện backend sau)
            fetch(`/posts/${postId}/delete`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                }
            }).then(res => {
                if (res.ok) {
                    // Xóa post khỏi DOM
                    const postCard = document.getElementById(`post-${postId}`);
                    if (postCard) postCard.remove();
                } else {
                    alert('Failed to delete post.');
                }
            });
        }
    }
};

window.PostActions = PostActions;
window.loadPostDetail = PostActions.loadPostDetail.bind(PostActions);

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    PostActions.initialize();
});
}
