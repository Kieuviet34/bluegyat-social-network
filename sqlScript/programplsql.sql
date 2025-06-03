CREATE OR REPLACE PACKAGE pkg_social_ops AS
  -------------------------------------------------------------------
  -- Phần 1: Comment
  -------------------------------------------------------------------
  -- 1.1. Thêm comment mới, trả về COMMENT_ID vừa tạo
  FUNCTION add_comment(
    p_post_id IN NUMBER,
    p_user_id IN NUMBER,
    p_content IN VARCHAR2
  ) RETURN NUMBER;

  -- 1.2. Sửa comment, trả về 1 nếu thành công, 0 nếu không tìm thấy hoặc không có quyền
  FUNCTION update_comment(
    p_comment_id IN NUMBER,
    p_user_id    IN NUMBER,
    p_content    IN VARCHAR2,
    p_img_url    IN VARCHAR2
  ) RETURN NUMBER;

  -- 1.3. Xóa comment, trả về 1 nếu thành công, 0 nếu không tìm thấy hoặc không có quyền
  FUNCTION delete_comment(
    p_comment_id IN NUMBER,
    p_user_id    IN NUMBER
  ) RETURN NUMBER;

  -- 1.4. Lấy số lượng comment của một post
  FUNCTION get_comment_count(
    p_post_id IN NUMBER
  ) RETURN NUMBER;


  -------------------------------------------------------------------
  -- Phần 2: Like
  -------------------------------------------------------------------
  -- 2.1. Toggle Like/Unlike, trả về số like mới của post
  FUNCTION toggle_like(
    p_post_id IN NUMBER,
    p_user_id IN NUMBER
  ) RETURN NUMBER;

  -- 2.2. Lấy số like của một post
  FUNCTION get_like_count(
    p_post_id IN NUMBER
  ) RETURN NUMBER;


  -------------------------------------------------------------------
  -- Phần 3: Post
  -------------------------------------------------------------------
  -- 3.1. Cập nhật post (chỉ chủ post mới sửa được), trả về 1 nếu thành công, 0 nếu sai quyền hoặc không tìm thấy
  FUNCTION update_post(
    p_post_id   IN NUMBER,
    p_user_id   IN NUMBER,
    p_content   IN CLOB,
    p_media_url IN VARCHAR2
  ) RETURN NUMBER;

  -- 3.2. Xóa post (chỉ chủ post mới xóa được), trả về 1 nếu thành công, 0 nếu sai quyền hoặc không tìm thấy
  FUNCTION delete_post(
    p_post_id IN NUMBER,
    p_user_id IN NUMBER
  ) RETURN NUMBER;


  -------------------------------------------------------------------
  -- Phần 4: User Profile
  -------------------------------------------------------------------
  -- 4.1. Cập nhật thông tin profile (full_name, email, avatar, cover), không trả về giá trị
  PROCEDURE update_profile(
    p_user_id         IN NUMBER,
    p_full_name       IN VARCHAR2,
    p_email           IN VARCHAR2,
    p_profile_img_url IN VARCHAR2,
    p_cover_img_url   IN VARCHAR2
  );


  -------------------------------------------------------------------
  -- Phần 5: Search & Discovery
  -------------------------------------------------------------------
  -- 5.1. Tìm kiếm posts theo username hoặc full_name, trả về SYS_REFCURSOR
  FUNCTION search_posts(
    p_q IN VARCHAR2
  ) RETURN SYS_REFCURSOR;

END pkg_social_ops;
/
CREATE OR REPLACE PACKAGE BODY pkg_social_ops AS

  -----------------------------------------------------------------------------
  -- Phần 1: Comment
  -----------------------------------------------------------------------------

  -- 1.1. add_comment: Thêm comment mới, trả về COMMENT_ID
  FUNCTION add_comment(
    p_post_id IN NUMBER,
    p_user_id IN NUMBER,
    p_content IN VARCHAR2
  ) RETURN NUMBER IS
    v_new_id NUMBER;
  BEGIN
    INSERT INTO COMMENTS (
      POST_ID,
      USER_ID,
      CONTENT,
      IMG_URL,
      CREATED_AT
    ) VALUES (
      p_post_id,
      p_user_id,
      p_content,
      NULL,
      SYSTIMESTAMP
    )
    RETURNING COMMENT_ID INTO v_new_id;

    RETURN v_new_id;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE_APPLICATION_ERROR(-20001, 'Cannot add comment: ' || SQLERRM);
  END add_comment;

  -- 1.2. update_comment: Sửa comment, trả về 1 nếu thành công, 0 nếu không
  FUNCTION update_comment(
    p_comment_id IN NUMBER,
    p_user_id    IN NUMBER,
    p_content    IN VARCHAR2,
    p_img_url    IN VARCHAR2
  ) RETURN NUMBER IS
    v_cnt NUMBER;
  BEGIN
    -- Kiểm tra quyền: chỉ chủ comment mới sửa được
    SELECT COUNT(*) INTO v_cnt
      FROM COMMENTS
     WHERE COMMENT_ID = p_comment_id
       AND USER_ID    = p_user_id;

    IF v_cnt = 0 THEN
      RETURN 0;  -- không tìm thấy hoặc không có quyền
    END IF;

    UPDATE COMMENTS
       SET CONTENT = p_content,
           IMG_URL  = p_img_url
     WHERE COMMENT_ID = p_comment_id
       AND USER_ID    = p_user_id;

    RETURN 1;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RETURN 0;
  END update_comment;

  -- 1.3. delete_comment: Xóa comment, trả về 1 nếu thành công, 0 nếu không
  FUNCTION delete_comment(
    p_comment_id IN NUMBER,
    p_user_id    IN NUMBER
  ) RETURN NUMBER IS
    v_cnt NUMBER;
  BEGIN
    -- Kiểm tra quyền
    SELECT COUNT(*) INTO v_cnt
      FROM COMMENTS
     WHERE COMMENT_ID = p_comment_id
       AND USER_ID    = p_user_id;

    IF v_cnt = 0 THEN
      RETURN 0;  -- không tìm thấy hoặc không có quyền
    END IF;

    DELETE FROM COMMENTS
     WHERE COMMENT_ID = p_comment_id
       AND USER_ID    = p_user_id;

    RETURN 1;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RETURN 0;
  END delete_comment;

  -- 1.4. get_comment_count: Lấy tổng số comment của một post
  FUNCTION get_comment_count(
    p_post_id IN NUMBER
  ) RETURN NUMBER IS
    v_cnt NUMBER;
  BEGIN
    SELECT COUNT(*) INTO v_cnt
      FROM COMMENTS
     WHERE POST_ID = p_post_id;
    RETURN v_cnt;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20002, 'Cannot get comment count: ' || SQLERRM);
  END get_comment_count;


  -----------------------------------------------------------------------------
  -- Phần 2: Like
  -----------------------------------------------------------------------------

  -- 2.1. toggle_like: Toggle between like/unlike, trả về số like mới
  FUNCTION toggle_like(
    p_post_id IN NUMBER,
    p_user_id IN NUMBER
  ) RETURN NUMBER IS
    v_exists      NUMBER;
    v_count_after NUMBER;
  BEGIN
    -- Kiểm tra nếu đã like rồi
    SELECT COUNT(*) INTO v_exists
      FROM LIKES
     WHERE POST_ID = p_post_id
       AND USER_ID = p_user_id;

    IF v_exists > 0 THEN
      DELETE FROM LIKES
       WHERE POST_ID = p_post_id
         AND USER_ID = p_user_id;
    ELSE
      INSERT INTO LIKES (
        USER_ID,
        POST_ID,
        LIKED_AT
      ) VALUES (
        p_user_id,
        p_post_id,
        SYSTIMESTAMP
      );
    END IF;

    COMMIT;

    -- Đếm lại số like
    SELECT COUNT(*) INTO v_count_after
      FROM LIKES
     WHERE POST_ID = p_post_id;

    RETURN v_count_after;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE_APPLICATION_ERROR(-20003, 'Cannot toggle like: ' || SQLERRM);
  END toggle_like;

  -- 2.2. get_like_count: Lấy tổng số like của post
  FUNCTION get_like_count(
    p_post_id IN NUMBER
  ) RETURN NUMBER IS
    v_cnt NUMBER;
  BEGIN
    SELECT COUNT(*) INTO v_cnt
      FROM LIKES
     WHERE POST_ID = p_post_id;
    RETURN v_cnt;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20004, 'Cannot get like count: ' || SQLERRM);
  END get_like_count;


  -----------------------------------------------------------------------------
  -- Phần 3: Post
  -----------------------------------------------------------------------------

  -- 3.1. update_post: Cập nhật nội dung và media của post, trả về 1 nếu thành công, 0 nếu không
  FUNCTION update_post(
    p_post_id   IN NUMBER,
    p_user_id   IN NUMBER,
    p_content   IN CLOB,
    p_media_url IN VARCHAR2
  ) RETURN NUMBER IS
    v_cnt NUMBER;
  BEGIN
    -- Kiểm tra exist và quyền: chỉ chủ post mới sửa
    SELECT COUNT(*) INTO v_cnt
      FROM POSTS
     WHERE POST_ID = p_post_id
       AND USER_ID = p_user_id;

    IF v_cnt = 0 THEN
      RETURN 0;
    END IF;

    UPDATE POSTS
       SET CONTENT   = p_content,
           MEDIA_URL = p_media_url
     WHERE POST_ID = p_post_id
       AND USER_ID = p_user_id;

    RETURN 1;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE_APPLICATION_ERROR(-20005, 'Cannot update post: ' || SQLERRM);
  END update_post;

  -- 3.2. delete_post: Xóa một post, trả về 1 nếu thành công, 0 nếu không
  FUNCTION delete_post(
    p_post_id IN NUMBER,
    p_user_id IN NUMBER
  ) RETURN NUMBER IS
    v_cnt NUMBER;
  BEGIN
    -- Kiểm tra exist và quyền
    SELECT COUNT(*) INTO v_cnt
      FROM POSTS
     WHERE POST_ID = p_post_id
       AND USER_ID = p_user_id;

    IF v_cnt = 0 THEN
      RETURN 0;
    END IF;

    -- Xóa thủ công các đối tượng con (nếu không dùng ON DELETE CASCADE):
    DELETE FROM POST_MEDIA WHERE POST_ID = p_post_id;
    DELETE FROM COMMENTS   WHERE POST_ID = p_post_id;
    DELETE FROM LIKES      WHERE POST_ID = p_post_id;

    DELETE FROM POSTS
     WHERE POST_ID = p_post_id
       AND USER_ID = p_user_id;

    RETURN 1;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE_APPLICATION_ERROR(-20006, 'Cannot delete post: ' || SQLERRM);
  END delete_post;


  -----------------------------------------------------------------------------
  -- Phần 4: User Profile
  -----------------------------------------------------------------------------

  -- 4.1. update_profile: Cập nhật full_name, email, avatar, cover
  PROCEDURE update_profile(
    p_user_id         IN NUMBER,
    p_full_name       IN VARCHAR2,
    p_email           IN VARCHAR2,
    p_profile_img_url IN VARCHAR2,
    p_cover_img_url   IN VARCHAR2
  ) IS
  BEGIN
    UPDATE SC_USERS
       SET FULL_NAME       = p_full_name,
           EMAIL           = p_email,
           PROFILE_IMG_URL = p_profile_img_url,
           COVER_IMG_URL   = p_cover_img_url
     WHERE USER_ID = p_user_id;

    COMMIT;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE_APPLICATION_ERROR(-20007, 'Cannot update profile: ' || SQLERRM);
  END update_profile;


  -----------------------------------------------------------------------------
  -- Phần 5: Search & Discovery
  -----------------------------------------------------------------------------

  -- 5.1. search_posts: trả về SYS_REFCURSOR các post thỏa mãn filter theo username/full_name
  FUNCTION search_posts(
    p_q IN VARCHAR2
  ) RETURN SYS_REFCURSOR IS
    c_cursor SYS_REFCURSOR;
    v_pattern VARCHAR2(200) := '%' || UPPER(p_q) || '%';
  BEGIN
    OPEN c_cursor FOR
      SELECT p.POST_ID,
             p.USER_ID,
             p.CONTENT,
             p.MEDIA_URL,
             p.CREATED_AT,
             u.FULL_NAME     AS AUTHOR_NAME,
             u.USERNAME      AS AUTHOR_USERNAME
        FROM POSTS p
        JOIN SC_USERS u ON p.USER_ID = u.USER_ID
       WHERE UPPER(u.USERNAME)   LIKE v_pattern
          OR UPPER(u.FULL_NAME) LIKE v_pattern
       ORDER BY p.CREATED_AT DESC;
    RETURN c_cursor;
  EXCEPTION
    WHEN OTHERS THEN
      RAISE_APPLICATION_ERROR(-20008, 'Search error: ' || SQLERRM);
  END search_posts;

END pkg_social_ops;
/
//trigger
///friend request trigger
CREATE OR REPLACE TRIGGER trg_after_insert_friendreq
AFTER INSERT ON FRIENDSHIPS
FOR EACH ROW
DECLARE
  v_actor   VARCHAR2(100);
  v_message VARCHAR2(4000);
BEGIN
  -- Chỉ xử lý khi status = 'PENDING'
  IF :NEW.STATUS = 'PENDING' THEN
    -- Lấy tên actor (người gửi request)
    SELECT FULL_NAME
      INTO v_actor
      FROM SC_USERS
     WHERE USER_ID = :NEW.USER_ID;

    v_message := v_actor || ' đã gửi lời mời kết bạn.';

    INSERT INTO NOTIFICATIONS (
      RECIPIENT_USER_ID,
      ACTOR_USER_ID,
      TYPE,
      ENTITY_ID,
      ENTITY_TYPE,
      MESSAGE,
      IS_READ
    ) VALUES (
      :NEW.FRIEND_ID,        -- người được mời
      :NEW.USER_ID,          -- người gửi request
      'FRIEND_REQUEST',      -- loại
      :NEW.USER_ID,          -- dùng USER_ID làm entity_id (có thể là FRIEND_ID)
      'FRIENDSHIP',
      v_message,
      'N'
    );
  END IF;
EXCEPTION
  WHEN OTHERS THEN
    -- Nếu gặp lỗi, chỉ bỏ qua (hoặc log nếu cần)
    NULL;
END trg_after_insert_friendreq;
/

//like trigger
CREATE OR REPLACE TRIGGER trg_after_insert_like
AFTER INSERT ON LIKES
FOR EACH ROW
DECLARE
  v_actor     VARCHAR2(100);
  v_message   VARCHAR2(4000);
  v_recipient NUMBER;
BEGIN
  -- Lấy tên actor (người like)
  SELECT FULL_NAME
    INTO v_actor
    FROM SC_USERS
   WHERE USER_ID = :NEW.USER_ID;

  -- Lấy chủ post (recipient)
  SELECT USER_ID
    INTO v_recipient
    FROM POSTS
   WHERE POST_ID = :NEW.POST_ID;

  v_message := v_actor || ' đã thích bài viết của bạn.';

  INSERT INTO NOTIFICATIONS (
    RECIPIENT_USER_ID,
    ACTOR_USER_ID,
    TYPE,
    ENTITY_ID,
    ENTITY_TYPE,
    MESSAGE,
    IS_READ
  ) VALUES (
    v_recipient,       -- chủ post sẽ nhận notification
    :NEW.USER_ID,      -- người like
    'LIKE',
    :NEW.POST_ID,      -- entity_id là POST_ID
    'POST',
    v_message,
    'N'
  );
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    NULL;  -- nếu không tìm thấy post
  WHEN OTHERS THEN
    NULL;  -- bỏ qua lỗi
END trg_after_insert_like;
/
//comment trigger
CREATE OR REPLACE TRIGGER trg_after_insert_comment
AFTER INSERT ON COMMENTS
FOR EACH ROW
DECLARE
  v_actor     VARCHAR2(100);
  v_message   VARCHAR2(4000);
  v_recipient NUMBER;
BEGIN
  -- Lấy tên actor (người comment)
  SELECT FULL_NAME
    INTO v_actor
    FROM SC_USERS
   WHERE USER_ID = :NEW.USER_ID;

  -- Lấy chủ post (recipient)
  SELECT USER_ID
    INTO v_recipient
    FROM POSTS
   WHERE POST_ID = :NEW.POST_ID;

  v_message := v_actor || ' đã bình luận trên bài viết của bạn.';

  INSERT INTO NOTIFICATIONS (
    RECIPIENT_USER_ID,
    ACTOR_USER_ID,
    TYPE,
    ENTITY_ID,
    ENTITY_TYPE,
    MESSAGE,
    IS_READ
  ) VALUES (
    v_recipient,       -- chủ post
    :NEW.USER_ID,      -- người comment
    'COMMENT',
    :NEW.POST_ID,      -- entity_id là POST_ID
    'POST',
    v_message,
    'N'
  );
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    NULL;  -- nếu không tìm thấy post
  WHEN OTHERS THEN
    NULL;  -- bỏ qua lỗi
END trg_after_insert_comment;
/

select * from posts;
select * from sc_users;
select * from likes;
select * from comments;