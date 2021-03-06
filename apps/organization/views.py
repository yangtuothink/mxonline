from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import CourseOrg, CityDict, Teacher
from .forms import UserAskForm
from operation.models import UserFavorite
from courses.models import Course


# 课程列表
class OrgView(View):

    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()
        # 机构城市
        all_citys = CityDict.objects.all()
        # 机构搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(
                Q(name__icontains=search_keywords) |
                Q(desc__icontains=search_keywords))
        # 热门机构
        hot_orgs = all_orgs.order_by("click_nums")[:3]
        # 取出筛选类别
        categroy = request.GET.get('ct', "")
        if categroy:
            all_orgs = all_orgs.filter(category=categroy)
        # 取出筛选城市
        city_id = request.GET.get('city', "")
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))
        # 学习人数 / 课程数 排序
        sort = request.GET.get("sort", "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")
        # 总机构个数
        org_nums = all_orgs.count()
        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_orgs, 5, request=request)
        orgs = p.page(page)
        return render(request, "org-list.html", {
            "all_orgs": orgs,
            "all_citys": all_citys,
            "org_nums": org_nums,
            "city_id": city_id,
            "categroy": categroy,
            "hot_orgs": hot_orgs,
            "sort": sort
        })


# 用户添加咨询
class AddUserAskView(View):
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            # 保存到数据库中
            user_ask = userask_form.save(commit=True)
            # 进行异步的提交,返回ajax操作
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


# 机构首页
class OrgHomeView(View):

    def get(self, request, org_id):
        current_page = "home"
        # 根据id取出课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 点击 + 1
        course_org.click_nums += 1
        course_org.save()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        # 取出所有机构课程，取出外键的值
        all_courses = course_org.course_set.all()[:3]
        # 取出所有机构讲师，取出外键的值
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html', {
            "all_courses": all_courses,
            "all_teachers": all_teachers,
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav
        })


# 机构课程列表页
class OrgCourseView(View):

    def get(self, request, org_id):
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_courses = course_org.course_set.all()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-course.html', {
            "all_courses": all_courses,
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav
        })


# 机构介绍页
class OrgDescView(View):

    def get(self, request, org_id):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav
        })


# 机构讲师页
class OrgTeacherView(View):

    def get(self, request, org_id):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teacher = course_org.teacher_set.all()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-teachers.html', {
            "all_teacher": all_teacher,
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav
        })


# 用户收藏
class AddFavView(View):
    def post(self, request):
        fav_id = request.POST.get("fav_id", 0)
        fav_type = request.POST.get("fav_type", 0)
        # 判断登录状态
        if not request.user.is_authenticated():
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        exit_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exit_records:
            # 记录存在, 取消收藏
            exit_records.delete()
            if int(fav_type) == 1:
                # 课程收藏数 - 1
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                # 课程机构收藏数 - 1
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(fav_type) == 3:
                # 讲师收藏数 - 1
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()
                if int(fav_type) == 1:
                    # 课程收藏数 + 1
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    # 课程机构收藏数 + 1
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    # 讲师收藏数 + 1
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()
                return HttpResponse('{"status":"fail", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错啦"}', content_type='application/json')


# 课程讲师列表页
class TercherListView(View):
    def get(self, request):
        # 所有讲师
        all_teachers = Teacher.objects.all()
        # 讲师搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(
                Q(name__icontains=search_keywords) |
                Q(work_company__icontains=search_keywords) |
                Q(work_position__icontains=search_keywords))
        # 教师人气排序
        sort = request.GET.get("sort", "")
        if sort:
            if sort == "hot":
                all_teachers = all_teachers.order_by("-click_nums")
        # 讲师排行榜
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]
        # 获取讲师数量
        teacher_num = all_teachers.count()
        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_teachers, 1, request=request)
        teachers = p.page(page)
        return render(request, "teachers-list.html", {
            "all_teachers": teachers,
            "sorted_teacher": sorted_teacher,
            "teacher_num": teacher_num,
            "sort": sort,
        })


# 课程讲师详情页
class TeacherDetailView(View):

    def get(self, request, teacher_id):
        # 当前讲师
        teacher = Teacher.objects.get(id=int(teacher_id))
        # 点击 + 1
        teacher.click_nums += 1
        teacher.save()
        # 讲师所有课程
        all_courses = Course.objects.filter(teacher=teacher)
        # 讲师排行
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]
        # 讲师 / 机构 收藏状态
        has_teacher_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
            has_teacher_faved = True
        has_org_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
            has_org_faved = True

        return render(request, "teacher-detail.html", {
            "teacher": teacher,
            "all_courses": all_courses,
            "sorted_teacher": sorted_teacher,
            "has_teacher_faved": has_teacher_faved,
            "has_org_faved": has_org_faved
        })
