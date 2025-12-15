#include <SDL2/SDL.h> 
#include <iostream>
#include <unordered_map>
#include <cmath>
#include <unordered_set>
using namespace std;


//pair hash function
struct hash_pair {
    template <class T1, class T2>
    size_t operator()(const pair<T1, T2>& p) const
    {
        // Hash the first element
        size_t hash1 = hash<T1>{}(p.first);
        // Hash the second element
        size_t hash2 = hash<T2>{}(p.second);
        // Combine the two hash values
        return hash1
               ^ (hash2 + 0x9e3779b9 + (hash1 << 6)
                  + (hash1 >> 2));
    }
};


constexpr int width = 600;
constexpr int height = 600;

void process(SDL_Event &event, SDL_Window* window, SDL_Renderer* renderer, bool* running,unordered_set<pair<int,int>,hash_pair>* sands, bool* ismouse, int* sandamt, bool* iswood,unordered_set<pair<int,int>,hash_pair>* woods){
    //function for processing game input
    while( SDL_PollEvent( &event ) ){
        switch( event.type ){
            //put different keys in here
            case SDL_KEYDOWN:
                case SDLK_ESCAPE:
                    (*running) = false;
                    SDL_DestroyRenderer(renderer);
                    SDL_DestroyWindow(window);
                    SDL_Quit();
                    break;
                break;
            case SDL_KEYUP:
                break;
            case SDL_MOUSEBUTTONDOWN:
                switch(event.button.button){
                    case SDL_BUTTON_LEFT:
                        (*ismouse) = true;
                        break;
                    case SDL_BUTTON_RIGHT:
                        (*iswood) = true;
                        break;
                    default:
                        break;
                }
                break;
            case SDL_MOUSEBUTTONUP:
                switch(event.button.button){
                    case SDL_BUTTON_LEFT: 
                        (*ismouse) = false; 
                        break;
                    case SDL_BUTTON_RIGHT:
                        (*iswood) = false;
                        break;
                    default:
                        break;
                }
                break;
            default:
                break;
      }
   }
   if ((*ismouse)){
        int x;
        int y;
        SDL_GetMouseState(&x,&y);
        int radius = 10; 
            
            for (int dx = -radius; dx <= radius; ++dx) {
                for (int dy = -radius; dy <= radius; ++dy) {
                    if (sqrt(dx * dx + dy * dy) <= radius) {
                        (*sands).insert(make_pair(x + dx,y + dy));
                    }
                }
            }
   }
   if ((*iswood)){
        int x;
        int y;
        SDL_GetMouseState(&x,&y);
        int radius = 15; 
            
            for (int dx = -radius; dx <= radius; ++dx) {
                for (int dy = -radius; dy <= radius; ++dy) {
                    if (sqrt(dx * dx + dy * dy) <= radius) {
                        (*woods).insert(make_pair(x + dx,y + dy));
                    }
                }
            }
   }
}


int main(void) {
    SDL_Event event;
    //random garbage off of the internet
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        printf("SDL_Init Error: %s\n", SDL_GetError());
        return 1;
    }

    SDL_Window* window = SDL_CreateWindow("Hello SDL", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, 0);
    if (window == NULL) {
        printf("SDL_CreateWindow Error: %s\n", SDL_GetError());
        return 1;
    }

    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (renderer == NULL) {
        printf("SDL_CreateRenderer Error: %s\n", SDL_GetError());
        return 1;
    }

    bool running = true;
    unordered_map<int,unordered_map<int,char>> grid;
    for (int x = 0; x < width; x++){
        for(int y = 0; y <height; y++){
            grid[x][y] = '0';
        }
    }
    unordered_set<pair<int,int>,hash_pair> sands;
    unordered_set<pair<int,int>,hash_pair> woods;
    int sandamt = 0;
    int t_length = 600;
    int t_width = 600;
    auto texture = SDL_CreateTexture(renderer, 
                  SDL_PIXELFORMAT_RGBA8888, 
                  SDL_TEXTUREACCESS_STREAMING, 
                  t_length, 
                  t_width);

    uint8_t *pixels;
    int pitch;
    uint8_t r = 255;  // red
    uint8_t g = 22;    // green
    uint8_t b = 33;    // blue
    uint8_t a = 255;  // alpa
    int gravity = 1;
    bool ismouse = false;
    bool iswood = false;
    //game loop
    while (running){
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        //pixels
        SDL_LockTexture(texture, NULL, (void **)&pixels, &pitch);
        unordered_set<pair<int,int>,hash_pair> tempsands = sands;
        int flipflop = 1;
        for (auto sand = sands.begin(); sand!= sands.end(); sand++){
            int x = (*sand).first;
            int y = (*sand).second;
            if (grid[x][y+1] == '0'){
                grid[x][y] = '0';
                grid[x][y+1] = 's';
                tempsands.erase((*sand));
                tempsands.insert(make_pair(x,y+1));
                int pixelIndex = ((y+gravity) * pitch) + (x * 4);
                pixels[pixelIndex] = 255;        
                pixels[pixelIndex + 1] = 33;    
                pixels[pixelIndex + 2] = 222;    
                pixels[pixelIndex + 3] = 255;    
                pixelIndex = (y * pitch) + (x * 4);
                pixels[pixelIndex] = 0;      
                pixels[pixelIndex + 1] = 0;    
                pixels[pixelIndex + 2] = 0;   
                pixels[pixelIndex + 3] = 0;    
            }else if (grid[(x+1)][y+1] == '0'){
                grid[x][y] = '0';
                grid[x+1][y+1] = 's';
                tempsands.erase((*sand));
                tempsands.insert(make_pair(x+1,y+1));
                int pixelIndex = ((y+1) * pitch) + ((x+1) * 4);
                pixels[pixelIndex] = 255;        
                pixels[pixelIndex + 1] = 33;   
                pixels[pixelIndex + 2] = 222;    
                pixels[pixelIndex + 3] = 255;    
                pixelIndex = ((*sand).second * pitch) + ((*sand).first * 4);
                pixels[pixelIndex] = 0;        
                pixels[pixelIndex + 1] = 0;    
                pixels[pixelIndex + 2] = 0;    
                pixels[pixelIndex + 3] = 0;    
            }else if (grid[x-1][y+1] == '0'){
                grid[x][y] = '0';
                grid[x-1][y+1] = 's';
                tempsands.erase((*sand));
                tempsands.insert(make_pair(x-1,y+1));
                int pixelIndex = ((y+1) * pitch) + ((x-1) * 4);
                pixels[pixelIndex] = 255;        
                pixels[pixelIndex + 1] = 33;   
                pixels[pixelIndex + 2] = 222;    
                pixels[pixelIndex + 3] = 255;    
                pixelIndex = (y * pitch) + (x * 4);
                pixels[pixelIndex] = 0;      
                pixels[pixelIndex + 1] = 0;    
                pixels[pixelIndex + 2] = 0;   
                pixels[pixelIndex + 3] = 0;   
            }else if (grid[x][y] == 'w'){
                if (grid[x-flipflop][y] == '0'){
                grid[x][y] = '0';
                grid[x-flipflop][y] = 's';
                tempsands.erase((*sand));
                tempsands.insert(make_pair(x-flipflop,y));
                int pixelIndex = ((y) * pitch) + ((x-flipflop) * 4);
                pixels[pixelIndex] = 255;        
                pixels[pixelIndex + 1] = 33;  
                pixels[pixelIndex + 2] = 222;    
                pixels[pixelIndex + 3] = 255;   
                pixelIndex = (y * pitch) + (x * 4);
                pixels[pixelIndex] = 0;        
                pixels[pixelIndex + 1] = 0;   
                pixels[pixelIndex + 2] = 0;    
                pixels[pixelIndex + 3] = 0;   
            }else if (grid[x+flipflop][y] == '0'){
                grid[x][y] = '0';
                grid[x+flipflop][y] = 's';
                tempsands.erase((*sand));
                tempsands.insert(make_pair(x+flipflop,y));
                int pixelIndex = ((y) * pitch) + ((x+flipflop) * 4);
                pixels[pixelIndex] = 255;        
                pixels[pixelIndex + 1] = 33;  
                pixels[pixelIndex + 2] = 222;  
                pixels[pixelIndex + 3] = 255;   
                pixelIndex = (y * pitch) + (x * 4);
                pixels[pixelIndex] = 0;       
                pixels[pixelIndex + 1] = 0;    
                pixels[pixelIndex + 2] = 0; 
                pixels[pixelIndex + 3] = 0;   
            }
           }            
            flipflop *= -1;


        }
        unordered_set<pair<int,int>,hash_pair> tempwoods = woods;
        for(auto wood = woods.begin(); wood!= woods.end(); wood++){
            int x = (*wood).first;
            int y = (*wood).second;
            tempwoods.erase((*wood));
            grid[x][y] = 'w';
            int pixelIndex = (y * pitch) + (x * 4);
            pixels[pixelIndex] = 255;   
            pixels[pixelIndex + 1] = 0;  
            pixels[pixelIndex + 2] = 75;   
            pixels[pixelIndex + 3] = 150;   
        }
        woods = tempwoods;
        sands = tempsands;
        SDL_UnlockTexture(texture);
        SDL_RenderClear(renderer);
        SDL_RenderCopy(renderer, texture, NULL, NULL);
        SDL_RenderPresent(renderer);
        process(event,window,renderer,&running,&sands,&ismouse, &sandamt, &iswood,&woods);
        }
    return 0;
}
        


