import random
from datetime import datetime, timedelta

from database import AsyncSessionLocal
from model.attachment import Attachment, Comment, Image
from model.board import Board, BoardCategory
from model.finance import Finance
from model.ideation import Ideation, Status, Theme
from model.invest import Investment, Investor
from model.user import Group, RoleEnum, User


async def create_mock():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                mock_data = get_mock_themes()
                mock_data += get_mock_investors()
                mock_data += get_mock_users()
                mock_data += get_mock_image()
                mock_data += get_mock_ideation()
                mock_data += get_mock_attachment()
                mock_data += get_mock_comment()
                mock_data += get_mock_board()
                mock_data += get_mock_finance()
                session.add_all(mock_data)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e


def get_mock_themes():
    return [
        Theme(
            id="theme_1",
            name="농업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/194/194041.png",
        ),
        Theme(
            id="theme_2",
            name="어업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/194/194049.png",
        ),
        Theme(
            id="theme_3",
            name="광업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/2582/2582355.png",
        ),
        Theme(
            id="theme_4",
            name="제조업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/3409/3409613.png",
        ),
        Theme(
            id="theme_5",
            name="건설업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/1995/1995591.png",
        ),
        Theme(
            id="theme_6",
            name="정보통신업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/1407/1407691.png",
        ),
        Theme(
            id="theme_7",
            name="운수업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/1876/1876050.png",
        ),
        Theme(
            id="theme_8",
            name="숙박업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/2331/2331970.png",
        ),
        Theme(
            id="theme_9",
            name="음식점업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/535/535285.png",
        ),
        Theme(
            id="theme_10",
            name="금융업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/3458/3458363.png",
        ),
        Theme(
            id="theme_11",
            name="보험업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/4227/4227973.png",
        ),
        Theme(
            id="theme_12",
            name="부동산업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/1828/1828469.png",
        ),
        Theme(
            id="theme_13",
            name="전기 가스 증기 및 수도사업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/2911/2911574.png",
        ),
        Theme(
            id="theme_14",
            name="보건업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/1883/1883981.png",
        ),
        Theme(
            id="theme_15",
            name="사회복지서비스업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/1077/1077012.png",
        ),
        Theme(
            id="theme_16",
            name="예술 스포츠 및 여가관련 서비스업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/2921/2921222.png",
        ),
        Theme(
            id="theme_17",
            name="교육서비스업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/2731/2731286.png",
        ),
        Theme(
            id="theme_18",
            name="도매 및 소매업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/1152/1152011.png",
        ),
        Theme(
            id="theme_19",
            name="연구개발업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/3280/3280989.png",
        ),
        Theme(
            id="theme_20",
            name="광고 및 시장 조사업",
            description="",
            image="https://cdn-icons-png.flaticon.com/512/2810/2810868.png",
        ),
    ]


def get_mock_image():
    return [
        Image(
            id="image_1",
            related_id="ideation_1",
            file_name="farming.jpg",
            file_path="https://www.publicdomainpictures.net/pictures/320000/nahled/farming.jpg",
        ),
        Image(
            id="image_2",
            related_id="ideation_2",
            file_name="organic-farming.jpg",
            file_path="https://www.publicdomainpictures.net/pictures/200000/nahled/organic-farming-1468283323ALH.jpg",
        ),
        Image(
            id="image_3",
            related_id="ideation_3",
            file_name="farm-technology.jpg",
            file_path="https://www.publicdomainpictures.net/pictures/290000/nahled/farm-technology.jpg",
        ),
        Image(
            id="image_4",
            related_id="ideation_4",
            file_name="agricultural-fields.jpg",
            file_path="https://www.publicdomainpictures.net/pictures/300000/nahled/agricultural-fields.jpg",
        ),
        Image(
            id="image_5",
            related_id="ideation_5",
            file_name="farm-robotics.jpg",
            file_path="https://www.publicdomainpictures.net/pictures/340000/nahled/farm-robotics.jpg",
        ),
        Image(
            id="image_6",
            related_id="ideation_6",
            file_name="fishing-boats.jpg",
            file_path="https://www.publicdomainpictures.net/pictures/30000/nahled/fishing-boats-12054570215cW6I.jpg",
        ),
        Image(
            id="image_7",
            related_id="ideation_7",
            file_name="fish-farming.jpg",
            file_path="https://www.publicdomainpictures.net/pictures/220000/nahled/fish-farming.jpg",
        ),
    ]


def get_mock_investors():
    return [
        Investor(
            id="investor_1",
            name="Sequoia Capital",
            description="Sequoia Capital은 실리콘 밸리의 대표적인 벤처 캐피탈입니다.",
            image="https://upload.wikimedia.org/wikipedia/commons/3/35/Sequoia_Capital_Logo.png",
            assets_under_management="10 billion USD",
            investment_count=1300,
        ),
        Investor(
            id="investor_2",
            name="Andreessen Horowitz",
            description="Andreessen Horowitz는 IT 산업에 주로 투자하는 벤처 캐피탈입니다.",
            image="https://upload.wikimedia.org/wikipedia/commons/a/ae/Andreessen_Horowitz_logo.png",
            assets_under_management="16.6 billion USD",
            investment_count=900,
        ),
        Investor(
            id="investor_3",
            name="Accel",
            description="Accel은 다양한 글로벌 스타트업에 투자하는 벤처 캐피탈입니다.",
            image="https://upload.wikimedia.org/wikipedia/commons/8/8b/Accel_Logo.png",
            assets_under_management="9 billion USD",
            investment_count=1300,
        ),
        Investor(
            id="investor_4",
            name="SoftBank Vision Fund",
            description="SoftBank Vision Fund는 세계 최대의 기술 투자 펀드입니다.",
            image="https://upload.wikimedia.org/wikipedia/commons/e/ec/SoftBank_Group_Logo.svg",
            assets_under_management="100 billion USD",
            investment_count=500,
        ),
        Investor(
            id="investor_5",
            name="Benchmark Capital",
            description="Benchmark Capital은 초기 단계 스타트업에 집중적으로 투자하는 벤처 캐피탈입니다.",
            image="https://upload.wikimedia.org/wikipedia/en/5/5d/Benchmark_Capital_logo.png",
            assets_under_management="3 billion USD",
            investment_count=500,
        ),
        Investor(
            id="investor_6",
            name="Lightspeed Venture Partners",
            description="Lightspeed는 주로 기술 및 소비자 관련 기업에 투자하는 벤처 캐피탈입니다.",
            image="https://upload.wikimedia.org/wikipedia/commons/4/4f/Lightspeed_Venture_Partners_logo.png",
            assets_under_management="7 billion USD",
            investment_count=800,
        ),
        Investor(
            id="investor_7",
            name="Kleiner Perkins",
            description="Kleiner Perkins는 실리콘 밸리의 선도적인 벤처 캐피탈입니다.",
            image="https://upload.wikimedia.org/wikipedia/commons/0/06/Kleiner_Perkins_logo.png",
            assets_under_management="8 billion USD",
            investment_count=900,
        ),
        Investor(
            id="investor_8",
            name="Index Ventures",
            description="Index Ventures는 전 세계의 기술 기업에 투자하는 벤처 캐피탈입니다.",
            image="https://upload.wikimedia.org/wikipedia/commons/7/75/Index_Ventures_logo.png",
            assets_under_management="6 billion USD",
            investment_count=700,
        ),
        Investor(
            id="investor_9",
            name="Union Square Ventures",
            description="Union Square Ventures는 초기 단계 스타트업에 투자하는 뉴욕 기반 벤처 캐피탈입니다.",
            image="https://upload.wikimedia.org/wikipedia/commons/c/ce/Union_Square_Ventures_logo.png",
            assets_under_management="5 billion USD",
            investment_count=600,
        ),
        Investor(
            id="investor_10",
            name="Tiger Global Management",
            description="Tiger Global Management는 전 세계 기술 및 소비자 분야에 집중 투자하는 투자 회사입니다.",
            image="https://upload.wikimedia.org/wikipedia/en/9/98/Tiger_Global_Management_logo.png",
            assets_under_management="60 billion USD",
            investment_count=1000,
        ),
    ]


def get_mock_users():
    users = []
    u1 = User(
        id="user_1",
        name="admin",
        email="admin@series0.com",
        role=RoleEnum.ADMIN,
        expertises="관리",
        group_id="group_1",
    )
    users.append(u1)
    u2 = User(
        id="user_2",
        name="황젠슨",
        email="test1@series0.com",
        role=RoleEnum.INVESTOR,
        expertises="핀테크,web3,블록체인",
        group_id="group_1",
    )
    users.append(u2)
    u3 = User(
        id="user_3",
        name="이사수",
        email="test2@series0.com",
        role=RoleEnum.INVESTOR,
        expertises="디자인,마케팅,서비스기획",
        group_id="group_1",
    )
    users.append(u3)
    u4 = User(
        id="user_4",
        name="올트먼",
        email="test3@series0.com",
        role=RoleEnum.INVESTOR,
        expertises="콘텐츠,AL,딥테크",
        group_id="group_1",
    )
    users.append(u4)
    for u in users:
        u.password = "12341234"
    g1 = Group(
        id="group_1",
        name="blackrock",
        description="",
        image="https://nimage.g-enews.com/phpwas/restmb_allidxmake.php?idx=5&simg=2023082910592808544c4c55f9b3d210178127232.jpg",
        users=users,
    )
    groups = [g1]
    return users + groups


def get_mock_ideation():
    return [
        # 농업 테마 (theme_1)
        Ideation(
            id="ideation_1",
            title="스마트 농업 시스템",
            content="스마트 기술을 활용한 효율적인 농업 관리 솔루션.",
            presentation_date=datetime.now() + timedelta(days=30),
            close_date=datetime.now() + timedelta(days=60),
            status=Status.IN_PROGRESS,
            view_count=0,
            theme_id="theme_1",  # 올바른 theme_id
            user_id="user_1",
            investment_goal=1000000,
            investment_terms="지분율 10%, 최소 투자금액 1,000원, 최대 100,000,000원",
            investments=[
                create_random_investment("ideation_1")
                for _ in range(random.randint(1, 5))
            ],
        ),
        Ideation(
            id="ideation_2",
            title="친환경 농업 기술",
            content="유기농 기술을 적용한 지속 가능한 농업 아이디어.",
            # 친환경 농업 이미지
            presentation_date=datetime.now() + timedelta(days=30),
            close_date=datetime.now() + timedelta(days=60),
            status=Status.IN_PROGRESS,
            view_count=0,
            theme_id="theme_1",
            user_id="user_1",
            investment_goal=1200000,
            investment_terms="지분율 15%, 최소 투자금액 1,000원, 최대 80,000,000원",
            investments=[
                create_random_investment("ideation_2")
                for _ in range(random.randint(1, 5))
            ],
        ),
        Ideation(
            id="ideation_3",
            title="드론을 활용한 농업 자동화",
            content="드론 기술을 사용한 효율적인 농업 생산 관리 시스템.",
            presentation_date=datetime.now() + timedelta(days=40),
            close_date=datetime.now() + timedelta(days=70),
            status=Status.IN_PROGRESS,
            view_count=0,
            theme_id="theme_1",
            user_id="user_1",
            investment_goal=1500000,
            investment_terms="지분율 20%, 최소 투자금액 5,000원, 최대 150,000,000원",
            investments=[
                create_random_investment("ideation_3")
                for _ in range(random.randint(1, 5))
            ],
        ),
        Ideation(
            id="ideation_4",
            title="데이터 기반의 농업 최적화",
            content="빅데이터와 AI를 통해 농작물 생산성 향상을 위한 솔루션.",
            presentation_date=datetime.now() + timedelta(days=25),
            close_date=datetime.now() + timedelta(days=55),
            status=Status.IN_PROGRESS,
            view_count=0,
            theme_id="theme_1",
            user_id="user_1",
            investment_goal=1800000,
            investment_terms="지분율 25%, 최소 투자금액 10,000원, 최대 200,000,000원",
            investments=[
                create_random_investment("ideation_4")
                for _ in range(random.randint(1, 5))
            ],
        ),
        Ideation(
            id="ideation_5",
            title="농업용 로봇 자동화",
            content="농업 작업을 효율적으로 자동화하는 로봇 기술 솔루션.",
            presentation_date=datetime.now() + timedelta(days=35),
            close_date=datetime.now() + timedelta(days=65),
            status=Status.IN_PROGRESS,
            view_count=0,
            theme_id="theme_1",
            user_id="user_1",
            investment_goal=2000000,
            investment_terms="지분율 30%, 최소 투자금액 15,000원, 최대 250,000,000원",
            investments=[
                create_random_investment("ideation_5")
                for _ in range(random.randint(1, 5))
            ],
        ),
        # 어업 테마 (theme_2)
        Ideation(
            id="ideation_6",
            title="해양 어류 자동 관리 시스템",
            content="해양 자원을 효율적으로 관리하는 자동화 어업 시스템.",
            presentation_date=datetime.now() + timedelta(days=20),
            close_date=datetime.now() + timedelta(days=50),
            status=Status.IN_PROGRESS,
            view_count=0,
            theme_id="theme_2",  # 어업 테마
            user_id="user_1",
            investment_goal=2500000,
            investment_terms="지분율 20%, 최소 투자금액 2,000원, 최대 300,000,000원",
            investments=[
                create_random_investment("ideation_6")
                for _ in range(random.randint(1, 5))
            ],
        ),
        Ideation(
            id="ideation_7",
            title="친환경 해양 양식 기술",
            content="환경에 영향을 최소화하는 해양 양식 기술.",
            presentation_date=datetime.now() + timedelta(days=40),
            close_date=datetime.now() + timedelta(days=70),
            status=Status.IN_PROGRESS,
            view_count=0,
            theme_id="theme_2",
            user_id="user_1",
            investment_goal=1800000,
            investment_terms="지분율 18%, 최소 투자금액 1,000원, 최대 200,000,000원",
            investments=[
                create_random_investment("ideation_7")
                for _ in range(random.randint(1, 5))
            ],
        ),
    ]


def create_random_investment(ideation_id):
    return Investment(
        ideation_id=ideation_id,
        investor_id=f"investor_{random.randint(1, 10)}",
        amount=random.randint(1000, 1000000),
        approval_status=True,
    )


def get_mock_attachment():
    return [
        Attachment(
            id="attachment_1",
            file_name="프로젝트_계획서.pdf",
            file_path="프로젝트_계획서.pdf",
            related_id="ideation_1",
        ),
        Attachment(
            id="attachment_2",
            file_name="투자_계획서.pdf",
            file_path="투자_계획서.pdf",
            related_id="ideation_1",
        ),
        Attachment(
            id="attachment_3",
            file_name="프로젝트_계획서.pdf",
            file_path="프로젝트_계획서.pdf",
            related_id="ideation_1",
        ),
    ]


def get_mock_comment():
    return [
        Comment(
            id="comment_1",
            content="투자하고 싶은 프로젝트입니다.",
            rating=5,
            related_id="ideation_1",
            user_id="user_2",
        ),
        Comment(
            id="comment_2",
            content="나도 투자하고 싶은 프로젝트다.",
            rating=4,
            related_id="ideation_1",
            user_id="user_3",
        ),
        Comment(
            id="comment_3",
            content="나두 투자하고 싶은 프로젝트다.2",
            rating=5,
            related_id="comment_2",
            user_id="user_4",
        ),
    ]


def get_mock_board():
    return [
        Board(
            id="board_1",
            category=BoardCategory.NOTICE,
            title="시리즈제로 리얼 리뷰 콘테스트 수상자 발표",
            content="""
            시리즈제로 리얼 리뷰 콘테스트 수상자가 발표되었습니다. 수상자는 1등부터 3등까지 총 3명입니다.
            1등은 100만원, 2등은 50만원, 3등은 30만원의 상금을 받게 됩니다.
            수상자들은 7월 1일까지 연락을 주시기 
            """,
            created_at=datetime(2024, 6, 25),
        ),
        Board(
            id="board_2",
            category=BoardCategory.EVENT,
            title="국내 최초 포토샵 팝업스토어! 포토샵 AI로 세계일주!",
            content="""
            최초의 포토샵 팝업스토어가 오픈합니다. 포토샵 AI로 세계일주를 떠나는 이벤트가 진행됩니다.
            7월 1일까지 진행되니 많은 관심 부탁드립니다.
            """,
            created_at=datetime(2024, 6, 24),
        ),
        Board(
            id="board_3",
            category=BoardCategory.EVENT,
            title="'리빙크리에이터' 단 3일간 최대 혜택 (2.16-2.18)",
            content="""
            단 3일간 리빙크리에이터에서 최대 혜택을 드립니다. 2월 16일부터 2월 18일까지 진행되니 많은 관심 부탁드립니다.
            오늘 하루만 무료배송 혜택도 놓치지 마세요!
            2월 16일부터 2월 18일까지 진행되니 많은 관심 부탁드립니다.
            """,
            created_at=datetime(2024, 5, 24),
        ),
        Board(
            id="board_4",
            category=BoardCategory.PRESS_RELEASE,
            title="시리즈제로 라이콘 육성을 위한 '시리즈제로 넥스트브랜드' 쇼케이스 개최",
            content="""
            시리즈제로 라이콘 육성을 위한 '시리즈제로 넥스트브랜드' 쇼케이스가 개최됩니다.
            7월 1일까지 진행되니 많은 관심 부탁드립니다.
            이번 쇼케이스에서는 시리즈제로 라이콘 육성을 위한 다양한 프로그램이 준비되어 있습니다.
            그러므로 많은 관심 부탁드립니다.
            """,
            created_at=datetime(2024, 3, 1),
        ),
    ]


def get_mock_finance():
    return [
        Finance(
            ideation_id="ideation_1",
            direct_material=10000.0,  # 직접재료비
            direct_expense=5000.0,  # 직접경비
            direct_labor=4000.0,  # 직접노무비
            manufacturing_cost=3000.0,  # 제조간접비
            profit_rate=15.0,  # 이익률
            sale_price=30000.0,  # 판매가격 (소비자가격)
            salary=60000.0,  # 급여
            office_rent=12000.0,  # 사무실 임차료
            ad_cost=8000.0,  # 광고선전비
            business_expense=5000.0,  # 업무추진비
            maintenance_cost=3000.0,  # 접대비
            contingency=2000.0,  # 예비비용
            total_expense=92000.0,  # 판관비 계 (연비용)
            salary_increase_rate=5.0,  # 급여 인상율
            office_rent_increase_rate=3.0,  # 사무실 임차료 인상율
            ad_cost_increase_rate=4.0,  # 광고선전비 인상율
            business_expense_increase_rate=2.0,  # 업무추진비 인상율
            maintenance_cost_increase_rate=1.5,  # 접대비 인상율
            contingency_increase_rate=2.0,  # 예비비 인상율
            trade_counts=[
                100,
                150,
                200,
                250,
                300,
                350,
                400,
                450,
                500,
                550,
            ],  # 거래발생 수 (연차별 리스트)
            employee_counts=[
                10,
                12,
                14,
                16,
                18,
                20,
                22,
                24,
                26,
                28,
            ],  # 직원 수 (연차별 리스트)
        ),
        Finance(
            ideation_id="ideation_2",
            direct_material=15000.0,  # 직접재료비
            direct_expense=7000.0,  # 직접경비
            direct_labor=4500.0,  # 직접노무비
            manufacturing_cost=4000.0,  # 제조간접비
            profit_rate=12.0,  # 이익률
            sale_price=35000.0,  # 판매가격 (소비자가격)
            salary=70000.0,  # 급여
            office_rent=15000.0,  # 사무실 임차료
            ad_cost=9000.0,  # 광고선전비
            business_expense=5500.0,  # 업무추진비
            maintenance_cost=3200.0,  # 접대비
            contingency=2500.0,  # 예비비용
            total_expense=105200.0,  # 판관비 계 (연비용)
            salary_increase_rate=6.0,  # 급여 인상율
            office_rent_increase_rate=4.0,  # 사무실 임차료 인상율
            ad_cost_increase_rate=3.5,  # 광고선전비 인상율
            business_expense_increase_rate=2.5,  # 업무추진비 인상율
            maintenance_cost_increase_rate=1.8,  # 접대비 인상율
            contingency_increase_rate=2.2,  # 예비비 인상율
            trade_counts=[
                120,
                180,
                240,
                300,
                360,
                420,
                480,
                540,
                600,
                660,
            ],  # 거래발생 수 (연차별 리스트)
            employee_counts=[
                11,
                13,
                15,
                17,
                19,
                21,
                23,
                25,
                27,
                29,
            ],  # 직원 수 (연차별 리스트)
        ),
    ]
