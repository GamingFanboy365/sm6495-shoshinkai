#include <stdlib.h>

#ifdef TARGET_WEB
#include <emscripten.h>
#include <emscripten/html5.h>
#endif

#include "sm64.h"

#include "game/memory.h"
#include "audio/external.h"

#include "gfx/gfx_pc.h"
#include "gfx/gfx_3ds.h"
#include "gfx/gfx_citro3d.h"

#include "audio/audio_api.h"
#include "audio/audio_null.h"
#include "audio/audio_3ds.h"


#include "configfile.h"

#include "compat.h"

#define CONFIG_FILE "sm64config.txt"

OSMesg gMainReceivedMesg;
OSMesgQueue gSIEventMesgQueue;

s8 gResetTimer;
s8 gNmiResetBarsTimer;
s8 gDebugLevelSelect;
s8 gShowProfiler;
s8 gShowDebugText;

static struct AudioAPI *audio_api;
static struct GfxWindowManagerAPI *wm_api;
static struct GfxRenderingAPI *rendering_api;

extern void gfx_run(Gfx *commands);
extern void thread5_game_loop(void *arg);
extern void create_next_audio_buffer(s16 *samples, u32 num_samples);
void game_loop_one_iteration(void);

void dispatch_audio_sptask(UNUSED struct SPTask *spTask) {
}

void set_vblank_handler(UNUSED s32 index, UNUSED struct VblankHandler *handler, UNUSED OSMesgQueue *queue, UNUSED OSMesg *msg) {
}

static uint8_t inited = 0;

#include "game/game_init.h" // for gGlobalTimer
void exec_display_list(struct SPTask *spTask) {
    if (!inited) {
        return;
    }
    gfx_run((Gfx *)spTask->task.t.data_ptr);
}

#define printf

#ifdef VERSION_EU
#define SAMPLES_HIGH 656
#define SAMPLES_LOW 640
#else
#define SAMPLES_HIGH 544
#define SAMPLES_LOW 528
#endif

void produce_one_frame(void) {
    gfx_start_frame();
    game_loop_one_iteration();
    
    int samples_left = audio_api->buffered();
    u32 num_audio_samples = samples_left < audio_api->get_desired_buffered() ? SAMPLES_HIGH : SAMPLES_LOW;
    //printf("Audio samples: %d %u\n", samples_left, num_audio_samples);
    static s16 audio_buffer[SAMPLES_HIGH * 2 * 2];
    for (int i = 0; i < 2; i++) {
        /*if (audio_cnt-- == 0) {
            audio_cnt = 2;
        }
        u32 num_audio_samples = audio_cnt < 2 ? 528 : 544;*/
        create_next_audio_buffer(audio_buffer + i * (num_audio_samples * 2), num_audio_samples);
    }
    //printf("Audio samples before submitting: %d\n", audio_api->buffered());
    audio_api->play((u8 *)audio_buffer, 2 * num_audio_samples * 4);
    
    gfx_end_frame();
}

#ifdef TARGET_WEB
static void em_main_loop(void) {
}

static void request_anim_frame(void (*func)(double time)) {
    EM_ASM(requestAnimationFrame(function(time) {
        dynCall("vd", $0, [time]);
    }), func);
}

static void on_anim_frame(double time) {
    static double target_time;

    time *= 0.03; // milliseconds to frame count (33.333 ms -> 1)

    if (time >= target_time + 10.0) {
        // We are lagging 10 frames behind, probably due to coming back after inactivity,
        // so reset, with a small margin to avoid potential jitter later.
        target_time = time - 0.010;
    }

    for (int i = 0; i < 2; i++) {
        // If refresh rate is 15 Hz or something we might need to generate two frames
        if (time >= target_time) {
            produce_one_frame();
            target_time = target_time + 1.0;
        }
    }

    request_anim_frame(on_anim_frame);
}
#endif

static void save_config(void) {
    configfile_save(CONFIG_FILE);
}

static void on_fullscreen_changed(bool is_now_fullscreen) {
    configFullscreen = is_now_fullscreen;
}

void main_func(void) {
#ifdef USE_SYSTEM_MALLOC
    main_pool_init();
    gGfxAllocOnlyPool = alloc_only_pool_init();
#else
    static u64 pool[0x165000/8 / 4 * sizeof(void *)];
    main_pool_init(pool, pool + sizeof(pool) / sizeof(pool[0]));
#endif
    gEffectsMemoryPool = mem_pool_init(0x4000, MEMORY_POOL_LEFT);

#ifndef TARGET_N3DS
    configfile_load(CONFIG_FILE);
    atexit(save_config);
#endif

#ifdef TARGET_WEB
    emscripten_set_main_loop(em_main_loop, 0, 0);
    request_anim_frame(on_anim_frame);
#endif

    wm_api = &gfx_3ds;
    rendering_api = &gfx_citro3d_api;

    gfx_init(wm_api, rendering_api, "Super Mario 64 Shoshinkai 1995", configFullscreen);
    
    wm_api->set_fullscreen_changed_callback(on_fullscreen_changed);
    
    if (audio_api == NULL && audio_3ds.init()) {
        audio_api = &audio_3ds;
    }
    if (audio_api == NULL) {
        audio_api = &audio_null;
    }

    audio_init();
    sound_init();

    thread5_game_loop(NULL);
#ifdef TARGET_WEB
    /*for (int i = 0; i < atoi(argv[1]); i++) {
        game_loop_one_iteration();
    }*/
    inited = 1;
#elif defined(TARGET_N3DS)
    inited = 1;
    // the 3DS window manager runs its own main loop until the app is closed
    wm_api->main_loop(produce_one_frame);
#else
    inited = 1;
    while (1) {
        wm_api->main_loop(produce_one_frame);
    }
#endif
}

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
int WINAPI WinMain(UNUSED HINSTANCE hInstance, UNUSED HINSTANCE hPrevInstance, UNUSED LPSTR pCmdLine, UNUSED int nCmdShow) {
    main_func();
    return 0;
}
#else
int main(UNUSED int argc, UNUSED char *argv[]) {
    main_func();
    return 0;
}
#endif
