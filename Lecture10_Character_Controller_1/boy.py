from pico2d import load_image
from state_machine import (statemachine, space_down, time_out,
                           start_event, right_down, right_up, left_down, left_up)
from pico2d import get_time, SDL_KEYDOWN, SDLK_a, SDLK_SPACE, SDLK_RIGHT, SDLK_LEFT, SDL_KEYUP

class Idle:
    @staticmethod
    def enter(boy, e):
        if left_up(e) or right_down(e):
            boy.action = 2
            boy.face_dir = -1
        elif right_up(e) or left_down(e) or start_event(e):
            boy.action = 3
            boy.face_dir = 1

        boy.frame = 0
        boy.dir = 0
        boy.start_time = get_time()

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 1:
            boy.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)

class Sleep:
    @staticmethod
    def enter(boy, e):
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:  # 오른쪽 방향보고 있는 상태
            boy.image.clip_composite_draw(
                boy.frame * 100, 300, 100, 100,
                3.141592 / 2,  # 90도 회전
                '',  # 좌우상하 반전
                boy.x - 25, boy.y - 25, 100, 100
            )
        elif boy.face_dir == -1:
            boy.image.clip_composite_draw(
                boy.frame * 100, 200, 100, 100,
                -3.141592 / 2,  # -90도 회전
                '',  # 좌우상하 반전
                boy.x + 25, boy.y - 25, 100, 100
            )

class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):
            boy.action = 1  # 오른쪽 달리기 애니메이션
            boy.dir = 1
        elif left_down(e) or right_up(e):
            boy.action = 0  # 왼쪽 달리기 애니메이션
            boy.dir = -1

        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 3  # 이동 속도

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(
            boy.frame * 100, boy.action * 100, 100, 100,
            boy.x, boy.y
        )


class AutoRun:
    @staticmethod
    def enter(boy, e):
        print("Entered AutoRun State")
        boy.dir = boy.face_dir  # 바라보는 방향으로 이동
        boy.frame = 0
        boy.speed = 10  # 속도를 증가시킴
        boy.scale = 1.5  # 크기를 증가시킴
        boy.action = 1 if boy.face_dir == 1 else 0  # 달리는 이미지로 설정
        boy.start_time = get_time()  # 타이머 시작

    @staticmethod
    def exit(boy, e):
        print("Exited AutoRun State")
        boy.speed = 3  # 원래 속도로 복구
        boy.scale = 1.0  # 원래 크기로 복구

    @staticmethod
    def do(boy):
        boy.x += boy.dir * boy.speed  # 속도를 적용하여 이동

        # 입력 이벤트 체크
        current_time = get_time()
        if current_time - boy.start_time > 5:  # 5초 경과
            boy.state_machine.add_event(('TIME_OUT', 0))  # Idle 상태로 전환

        if boy.x > 800:  # 오른쪽 끝에 도달하면 방향 전환
            boy.dir = -1
            boy.face_dir = -1  # 방향 전환
            boy.action = 0  # 왼쪽 애니메이션으로 변경
        elif boy.x < 0:  # 왼쪽 끝에 도달하면 방향 전환
            boy.dir = 1
            boy.face_dir = 1  # 방향 전환
            boy.action = 1  # 오른쪽 애니메이션으로 변경
        boy.frame = (boy.frame + 1) % 8  # 프레임 업데이트

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(
            boy.frame * 100, boy.action * 100, 100, 100,
            boy.x, boy.y, 100 * boy.scale, 100 * boy.scale  # 크기를 반영
        )





class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = statemachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Idle: {
                    right_down: Run,
                    left_down: Run,
                    left_up: Run,
                    right_up: Run,
                    time_out: Sleep,
                    self.auto_run_key_down: AutoRun,  # A 키 입력 처리 추가
                },
                Run: {
                    right_down: Idle,
                    left_down: Idle,
                    right_up: Idle,
                    left_up: Idle,
                },
                AutoRun: {
                    right_down: Run,
                    left_down: Run,
                },
                Sleep: {
                    right_down: Run,
                    left_down: Run,
                    right_up: Run,
                    left_up: Run,
                    space_down: Idle,
                },
            }
        )

    def auto_run_key_down(self, e):
        return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.add_event(('INPUT', event))
        if self.state_machine.cur_state == AutoRun:
            # 타이머 초기화
            self.start_time = get_time()

    def draw(self):
        self.state_machine.draw()


