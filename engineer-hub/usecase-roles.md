# Tài liệu Use Case - Roles trong EngineerHub

## Tổng quan hệ thống

**EngineerHub** là hệ thống quản lý nhân lực kỹ sư, hỗ trợ đội sales tìm kiếm kỹ sư phù hợp cho khách hàng và giúp kỹ sư tự quản lý thông tin cá nhân.

---

## Danh sách Roles

| Role | Mô tả | Sections có quyền truy cập |
|------|-------|---------------------------|
| **Sales** | Nhân viên sales / quản lý | SALES Tools + Quản lý + Kỹ sư |
| **Engineer** | Kỹ sư trong hệ thống | Kỹ sư + Quản lý (giới hạn) |

---

## Role: Sales (Nhân viên Sales / Quản lý)

### Mô tả
Người dùng có quyền Sales là nhân viên kinh doanh hoặc quản lý, có trách nhiệm tìm kiếm và giới thiệu kỹ sư phù hợp cho các dự án của khách hàng.

**Ví dụ người dùng:** Tanaka Kenji - Sales Manager · JP

---

### UC-S01: Xem Sales Dashboard

**Mục tiêu:** Nắm tổng quan nhanh về trạng thái nhân lực hiện tại

**Luồng chính:**
1. Sales đăng nhập vào hệ thống
2. Hệ thống hiển thị Dashboard với các chỉ số tổng quan:
   - Số kỹ sư đang rảnh ngay
   - Số kỹ sư rảnh một phần
   - Số kỹ sư sắp rảnh trong 30 ngày
   - Tổng số kỹ sư
   - Utilization Rate (JP / VN)
   - Số kỹ sư có thể onsite Nhật
3. Sales xem danh sách kỹ sư đang rảnh
4. Sales xem cảnh báo & chú ý (alerts)
5. Sales xem biểu đồ utilization và top skills toàn công ty

**Kết quả:** Sales có cái nhìn tổng quan để lập kế hoạch sales

---

### UC-S02: Tìm kiếm kỹ sư bằng AI (AI Search)

**Mục tiêu:** Tìm nhanh kỹ sư phù hợp nhất dựa trên yêu cầu của khách hàng

**Luồng chính:**
1. Sales nhận được Job Description (JD) từ khách hàng
2. Sales mở trang AI Search
3. Sales dán nội dung JD / yêu cầu dự án vào ô nhập liệu
4. Sales nhấn nút "Phân tích & Tìm kiếm"
5. AI phân tích yêu cầu và hiển thị kết quả phân tích (tech stack, level, v.v.)
6. Hệ thống hiển thị danh sách kỹ sư phù hợp kèm % match
7. Sales xem profile chi tiết của từng kỹ sư
8. Sales chọn kỹ sư phù hợp
9. Sales tạo Proposal từ danh sách đã chọn

**Luồng thay thế:**
- Không tìm thấy kỹ sư phù hợp → Hệ thống thông báo "Không tìm thấy kỹ sư phù hợp"
- Sales dùng ví dụ nhanh (quick example) để thử tính năng

**Kết quả:** Sales có danh sách kỹ sư phù hợp để giới thiệu cho khách hàng

---

### UC-S03: Xem lịch trống kỹ sư (Availability Timeline)

**Mục tiêu:** Xem và lập kế hoạch về thời điểm kỹ sư có thể tham gia dự án

**Luồng chính:**
1. Sales mở trang Availability Timeline
2. Hệ thống hiển thị biểu đồ Gantt/Timeline 6 tháng tới
3. Sales lọc theo:
   - Tên kỹ sư
   - Kỹ năng cụ thể
   - Chỉ hiện kỹ sư Mobilizable (có thể onsite JP)
4. Sales xem trạng thái từng kỹ sư (rảnh / 50% rảnh / bận)
5. Sales xem số lượng kỹ sư rảnh tổng hợp ở footer

**Kết quả:** Sales biết kỹ sư nào sẵn sàng và vào thời điểm nào

---

### UC-S04: Tạo Proposal cho khách hàng

**Mục tiêu:** Tổng hợp thông tin kỹ sư thành tài liệu proposal gửi khách hàng

**Luồng chính:**
1. Sales chọn các kỹ sư từ kết quả AI Search (UC-S02)
2. Sales mở trang Proposal
3. Hệ thống hiển thị danh sách kỹ sư đã chọn
4. Sales nhập thông tin:
   - Tên khách hàng
   - Tên dự án
5. Sales nhấn "Tạo Proposal"
6. Hệ thống tạo proposal với thông tin đầy đủ
7. Sales xem trước (preview) tài liệu
8. Sales tải về file PDF

**Kết quả:** File proposal PDF sẵn sàng gửi cho khách hàng

---

### UC-S05: Quản lý danh sách kỹ sư

**Mục tiêu:** Xem và quản lý toàn bộ thông tin kỹ sư trong hệ thống

**Luồng chính:**
1. Sales mở trang Danh sách Kỹ sư (Engineers)
2. Hệ thống hiển thị danh sách theo dạng bảng hoặc thẻ (card)
3. Sales lọc theo tên / ID
4. Sales xem thông tin từng kỹ sư:
   - Địa điểm (JP / VN)
   - Level (Junior / Middle / Senior / Lead)
   - Kỹ năng chính
   - Trạng thái (rảnh / bận)
   - Workload
   - Điểm đánh giá
5. Sales xem chi tiết kỹ sư (thông tin, kỹ năng, chứng chỉ, trạng thái mobilization)
6. Quản lý thêm / xóa kỹ sư
7. Export danh sách ra file

**Kết quả:** Quản lý đầy đủ thông tin nhân lực

---

### UC-S06: Xem Skill Matrix

**Mục tiêu:** Phân tích năng lực kỹ thuật tổng thể của đội ngũ kỹ sư

**Luồng chính:**
1. Sales / Quản lý mở trang Skill Matrix
2. Hệ thống hiển thị ma trận kỹ năng (tên kỹ sư × kỹ năng)
3. Người dùng lọc theo:
   - Tên kỹ sư
   - Level tối thiểu (Lv1-Lv5)
   - Danh mục kỹ năng
   - Chỉ kỹ sư đang rảnh
4. Người dùng chuyển đổi giữa chế độ xem Ma trận và Biểu đồ
5. Hệ thống hiển thị thống kê footer:
   - Số người có kỹ năng ở mức Lv≥3
   - Số chuyên gia Lv5

**Kết quả:** Nắm rõ phân bổ kỹ năng để đưa ra quyết định nhân sự

---

## Role: Engineer (Kỹ sư)

### Mô tả
Người dùng có quyền Engineer là các kỹ sư trong công ty. Họ chỉ có thể quản lý thông tin của chính mình và không có quyền truy cập vào các công cụ sales.

**Ví dụ người dùng:** Nguyen Van An - Senior Engineer · ENG-001

---

### UC-E01: Xem và cập nhật Profile cá nhân

**Mục tiêu:** Kỹ sư tự quản lý thông tin nghề nghiệp của mình

**Luồng chính:**
1. Kỹ sư đăng nhập vào hệ thống
2. Hệ thống hiển thị trang Profile của tôi
3. Kỹ sư xem thông tin hiện tại:
   - Thông tin cơ bản (tên, ID, location, level, team, bucho)
   - Danh sách kỹ năng kèm level và số năm kinh nghiệm
   - Chứng chỉ đã có
   - Dự án đang tham gia
   - Ghi chú
4. Kỹ sư cập nhật thông tin kỹ năng:
   - Thêm kỹ năng mới
   - Cập nhật level kỹ năng
   - Cập nhật số năm kinh nghiệm
5. Hệ thống hiển thị banner thông báo "Có thay đổi mới chưa gửi"
6. Kỹ sư nhấn "Gửi cập nhật cho Bucho" (gửi cho quản lý trực tiếp)
7. Hệ thống xác nhận đã gửi thành công

**Luồng thay thế:**
- Kỹ sư hủy thay đổi → Dữ liệu được reset về trạng thái ban đầu

**Kết quả:** Thông tin profile được cập nhật và gửi cho quản lý phê duyệt

---

### UC-E02: Quản lý chứng chỉ

**Mục tiêu:** Kỹ sư lưu trữ và cập nhật danh sách chứng chỉ chuyên môn

**Luồng chính:**
1. Kỹ sư vào tab "Chứng chỉ" trong Profile
   **HOẶC** mở trang Chứng chỉ của tôi (certs.html)
2. Kỹ sư xem danh sách chứng chỉ hiện có
3. Kỹ sư thêm chứng chỉ mới:
   - Tải lên file chứng chỉ (PDF / hình ảnh)
   - Nhập tên chứng chỉ, ngày cấp
4. Kỹ sư xóa chứng chỉ không còn hiệu lực

**Kết quả:** Hồ sơ chứng chỉ được cập nhật, hiển thị trên profile khi sales tìm kiếm

---

### UC-E03: Xem Skill Matrix (đọc)

**Mục tiêu:** Kỹ sư xem năng lực tổng thể của đội ngũ để định hướng phát triển

**Luồng chính:**
1. Kỹ sư mở trang Skill Matrix (thuộc section MANAGE)
2. Kỹ sư xem ma trận kỹ năng toàn bộ kỹ sư
3. Kỹ sư tìm kiếm, lọc để xem so sánh với đồng nghiệp
4. Kỹ sư xem biểu đồ phân bổ kỹ năng toàn công ty

**Lưu ý:** Kỹ sư chỉ có quyền đọc, không chỉnh sửa dữ liệu người khác

**Kết quả:** Kỹ sư biết mình cần phát triển kỹ năng nào để phù hợp với nhu cầu công ty

---

## Bảng tổng hợp quyền truy cập theo Role

| Trang / Tính năng | Sales | Engineer |
|-------------------|:-----:|:--------:|
| **SALES TOOLS** | | |
| Dashboard (tổng quan nhân lực) | ✅ | ❌ |
| AI Search (tìm kỹ sư bằng AI) | ✅ | ❌ |
| Availability Timeline (lịch trống) | ✅ | ❌ |
| Tạo Proposal | ✅ | ❌ |
| **QUẢN LÝ** | | |
| Danh sách Kỹ sư (xem) | ✅ | ❌ |
| Danh sách Kỹ sư (thêm/xóa/export) | ✅ | ❌ |
| Skill Matrix | ✅ | ✅ (đọc) |
| **KỸ SƯ** | | |
| Profile cá nhân (xem & sửa) | ✅ | ✅ (chỉ của mình) |
| Chứng chỉ (xem & thêm) | ✅ | ✅ (chỉ của mình) |

---

## Ghi chú kiến trúc

- Phân quyền hiện tại được thực hiện ở **frontend** thông qua `document.body.dataset.role`
- Sidebar navigation được render động theo role bằng hàm `renderSidebar(role)` trong [engineer-hub/js/components.js](../engineer-hub/js/components.js)
- Role `'sales'` hiển thị tất cả sections: SALES + MANAGE + ENGINEER
- Role `'engineer'` chỉ hiển thị: ENGINEER + MANAGE
- Hệ thống hỗ trợ đa ngôn ngữ: Tiếng Việt và Tiếng Nhật
