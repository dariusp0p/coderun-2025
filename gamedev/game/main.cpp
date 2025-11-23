#include <iostream>
#include <vector>
#include <ctime>
#include <cmath>

#include <SDL3/SDL.h>
#include <glm/glm.hpp>

#include "circle.h"

constexpr int WINDOW_WIDTH{800};
constexpr int WINDOW_HEIGHT{800};

constexpr float PADDLE_SPEED = 500.0f;
constexpr float BALL_SPEED = 450.0f;

constexpr int BRICK_COLS = 17;
constexpr int BRICK_ROWS = 3;
constexpr float BRICK_HEIGHT = 20.0f;
constexpr float TOP_MARGIN = 100.0f;

struct RectEntity {
    glm::vec2 center;
    glm::vec2 size; // lungime , latime
    SDL_Color color;
    bool active = true;

    void draw(SDL_Renderer *r) const {
        if (!active) return;
        SDL_SetRenderDrawColor(r, color.r, color.g, color.b, color.a);
        SDL_FRect rect{
            center.x - size.x * 0.5f,
            center.y - size.y * 0.5f,
            size.x,
            size.y
        };
        SDL_RenderFillRect(r, &rect);
        SDL_SetRenderDrawColor(r, 0, 0, 0, 255);
        SDL_RenderRect(r, &rect);
    }
};

struct Brick : RectEntity {
    int lives = 1;

    void updateColor() {
        if (lives >= 3) color = {0, 255, 0, 255};
        else if (lives == 2) color = {255, 255, 0, 255};
        else color = {255, 0, 0, 255};
    }
};

SDL_Window *window{nullptr};
SDL_Renderer *renderer{nullptr};
SDL_Event currentEvent;
bool quit{false};

int winW_px = WINDOW_WIDTH, winH_px = WINDOW_HEIGHT;
int winW = WINDOW_WIDTH, winH = WINDOW_HEIGHT;
float displayScale = 1.0f;

RectEntity paddle;
Circle ball;
glm::vec2 ballVel{0.0f, 0.0f};
bool ballOnPaddle = true;

bool gameOver = false;
bool gameWon = false;

std::vector<Brick> bricks;

float deg2rad(float deg) {
    // conversteste unghiuri din grade in radiani
    return deg * (3.1415926535f / 180.0f);
}


// verifica daca mingea loveste un brick
// true - daca este coliziune
// false altfel
// in out normal seteaza directia din care a vent bila
bool circleRectCollision(const Circle &c, const RectEntity &re, glm::vec2 &outNormal) {
    float rx0 = re.center.x - re.size.x * 0.5f;
    float ry0 = re.center.y - re.size.y * 0.5f;
    float rx1 = re.center.x + re.size.x * 0.5f;
    float ry1 = re.center.y + re.size.y * 0.5f;

    float closestX = std::max(rx0, std::min(c.pos.x, rx1));
    float closestY = std::max(ry0, std::min(c.pos.y, ry1));

    float dx = c.pos.x - closestX;
    float dy = c.pos.y - closestY;

    if (dx * dx + dy * dy <= c.radius * c.radius) {
        float overlapX = std::min(c.pos.x + c.radius - rx0, rx1 - (c.pos.x - c.radius));
        float overlapY = std::min(c.pos.y + c.radius - ry0, ry1 - (c.pos.y - c.radius));

        if (overlapX < overlapY) {
            if (c.pos.x < re.center.x) {
                outNormal.x = -1.0f; // mingea a venit din stanga
            } else {
                outNormal.x = 1.0f; // mingea a venit din dreapta
            }
            outNormal.y = 0.0f;
        } else {
            if (c.pos.y < re.center.y) {
                outNormal.y = -1.0f; // mingea a venit de sus
            } else {
                outNormal.y = 1.0f; // a venit de jos
            }
            outNormal.x = 0.0f;
        }
        return true;
    }
    return false;
}

void spawnBricks() {
    bricks.clear();

    float brickW = (float) winW / BRICK_COLS;
    float startY = TOP_MARGIN + BRICK_HEIGHT * 0.5f;

    for (int row = 0; row < BRICK_ROWS; row++) {
        for (int col = 0; col < BRICK_COLS; col++) {
            Brick b;
            b.size = {brickW, BRICK_HEIGHT};
            b.center = {
                brickW * (col + 0.5f),
                startY + row * (BRICK_HEIGHT + 10.0f)
            };

            if (row == 0) {
                b.lives = 1;
            } else if (row == 1) {
                b.lives = 2;
            } else {
                b.lives = 3;
            }

            b.updateColor();
            b.active = true;

            bricks.push_back(b);
        }
    }
}

// pune mingea pe paleta si o opreste
// folosita la inceperea jocului si la fiecare resetare
void resetBallOnPaddle() {
    ballOnPaddle = true;
    ballVel = {0.0f, 0.0f};

    ball.radius = 10.0f;
    ball.color = {255, 165, 0, 255};
    ball.pos = {
        paddle.center.x,
        paddle.center.y - paddle.size.y * 0.5f - ball.radius
    };
}

bool initWindow() {
    bool success{true};
    if (!SDL_Init(SDL_INIT_VIDEO)) {
        SDL_Log("SDL initialization failed: %s\n", SDL_GetError());
        success = false;
    } else {
        displayScale = SDL_GetDisplayContentScale(1);

        if (!SDL_CreateWindowAndRenderer(
            "Block Breaker HARD",
            static_cast<int>(displayScale * WINDOW_WIDTH),
            static_cast<int>(displayScale * WINDOW_HEIGHT),
            0,
            &window, &renderer)) {
            SDL_Log("Failed to create window and renderer: %s\n", SDL_GetError());
            success = false;
        } else {
            SDL_SetRenderScale(renderer, displayScale, displayScale);
            SDL_GetWindowSize(window, &winW_px, &winH_px);
            winW = static_cast<int>(winW_px / displayScale);
            winH = static_cast<int>(winH_px / displayScale);
            success = true;
        }
    }
    return success;
}

void initGame() {
    paddle.size = {100.0f, 25.0f};
    paddle.center = {winW * 0.5f, winH - 40.0f};
    paddle.color = {0, 0, 255, 255};
    paddle.active = true;

    spawnBricks();
    resetBallOnPaddle();

    gameOver = false;
    gameWon = false;
}

void processEvents() {
    while (SDL_PollEvent(&currentEvent)) {
        if (currentEvent.type == SDL_EVENT_QUIT) quit = true;

        if (currentEvent.type == SDL_EVENT_KEY_DOWN) {
            if (currentEvent.key.key == SDLK_SPACE && !currentEvent.key.repeat && !gameOver && !gameWon) {
                if (ballOnPaddle) {
                    ballOnPaddle = false;
                    ballVel = {0.0f, -BALL_SPEED};
                }
            }
            if (currentEvent.key.key == SDLK_R && (gameOver || gameWon)) {
                initGame();
            }
        }
    }
}

void update(float dt) {
    if (gameOver || gameWon) return;

    const bool *keys = SDL_GetKeyboardState(nullptr);
    if (keys[SDL_SCANCODE_LEFT]) paddle.center.x -= PADDLE_SPEED * dt;
    if (keys[SDL_SCANCODE_RIGHT]) paddle.center.x += PADDLE_SPEED * dt;

    // verificarea daca paleta iese din ecran
    float halfW = paddle.size.x * 0.5f;
    if (paddle.center.x - halfW < 0) paddle.center.x = halfW;
    if (paddle.center.x + halfW > winW) paddle.center.x = winW - halfW;

    // mingea sta pe paleta pana se apsa space
    if (ballOnPaddle) {
        ball.pos.x = paddle.center.x;
        ball.pos.y = paddle.center.y - paddle.size.y * 0.5f - ball.radius;
        return;
    }

    ball.pos += ballVel * dt;

    // bounce-ul bilei
    if (ball.pos.x - ball.radius <= 0) {
        ball.pos.x = ball.radius;
        ballVel.x *= -1;
    }
    if (ball.pos.x + ball.radius >= winW) {
        ball.pos.x = winW - ball.radius;
        ballVel.x *= -1;
    }
    if (ball.pos.y - ball.radius <= 0) {
        ball.pos.y = ball.radius;
        ballVel.y *= -1;
    }

    // conditia cand bila ajunge jos
    if (ball.pos.y - ball.radius > winH) {
        gameOver = true;
        paddle.color = {255, 0, 0, 255};
        return;
    }

    glm::vec2 n;
    if (circleRectCollision(ball, paddle, n) && ballVel.y > 0) {
        // daca bla atinge paleta si se misca in jos
        float rel = (ball.pos.x - paddle.center.x) / (paddle.size.x * 0.5f);
        // rel = cat de la stanga sau dreapta a paletei a lovit bila
        // -1 = stanga, 0 = mijloc, 1 = dreapta
        rel = std::max(-1.0f, std::min(rel, 1.0f));

        float angleDeg = rel * 80.0f;
        float angleRad = deg2rad(angleDeg);

        glm::vec2 dir{std::sin(angleRad), -std::cos(angleRad)};
        // calculam directia noua in care pleaca bila
        // sin = miscarea pe x, cos = miscarea pe y
        ballVel = dir * BALL_SPEED;

        ball.pos.y = paddle.center.y - paddle.size.y * 0.5f - ball.radius - 0.5f;
    }

    for (auto &b: bricks) {
        if (!b.active) continue;

        glm::vec2 bn;
        if (circleRectCollision(ball, b, bn)) {
            if (glm::dot(ballVel, bn) > 0.0f) {
                // daca dot > 0 inseamna ca bila deja se misca in directia normala
                continue;
            }

            if (bn.x != 0.0f) ballVel.x *= -1;
            if (bn.y != 0.0f) ballVel.y *= -1;
            // in functie de directia normalei, intorc vitza pe x sau pe y

            ball.pos += bn * (ball.radius + 0.5f);

            b.lives--;
            if (b.lives <= 0) {
                b.active = false;
            } else {
                b.updateColor();
            }

            break;
        }
    }


    bool anyAlive = false;
    for (auto &b: bricks)
        if (b.active) {
            anyAlive = true;
            break;
        }

    if (!anyAlive) {
        gameWon = true;
        paddle.color = {0, 255, 0, 255};
        ball.radius = 0.0f;
    }
}

void drawFrame() {
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
    SDL_RenderClear(renderer);

    paddle.draw(renderer);
    for (auto &b: bricks) b.draw(renderer);
    if (!gameWon) ball.draw(renderer);

    SDL_RenderPresent(renderer);
}

void cleanup() {
    if (renderer) {
        SDL_DestroyRenderer(renderer);
        renderer = nullptr;
    }
    if (window) {
        SDL_DestroyWindow(window);
        window = nullptr;
    }
    SDL_Quit();
}

int main() {
    srand((unsigned) time(nullptr));

    if (!initWindow()) {
        std::cout << "Failed to initialize" << std::endl;
        return -1;
    }
    SDL_zero(currentEvent);
    initGame();

    Uint64 lastTicks = SDL_GetTicks();

    const float FIXED_DT = 1.0f / 120.0f;
    // fac update logic la fiecare 1/120 secunde
    float acc = 0;
    // accumulator care tine cat timp real s-a strans si trebuie procesat

    while (!quit) {
        Uint64 now = SDL_GetTicks();
        float frameDt = (now - lastTicks) / 1000.0f;
        // daca jocul se miscra prea greu din cauza altor surse, limitez timpul
        lastTicks = now;

        frameDt = std::min(frameDt, 0.25f);
        acc += frameDt;
        processEvents();
        while (acc >= FIXED_DT) {
            // fac updateul jocului in pasi mici pt a previne teleportari
            update(FIXED_DT); //si mentine coliziunile precise chiar daca exista o sursa de lag
            acc -= FIXED_DT;
        }
        drawFrame();
    }

    cleanup();
    return 0;
}
