import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import time
import math
import ctypes

class App:

    def __init__(self) -> None:
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((1280, 720), pygame.OPENGL | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        # Initialize OpenGL
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        # Load and use shaders from files
        self.shader = self.create_shader("shaders/vertex.vert", "shaders/fragment.frag")
        glUseProgram(self.shader)
        
        # Set texture unit 0 as active uniform sampler location for texture named 'imageTexture' in fragment shader
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        
        # Initialize triangle
        self.triangle = Triangle()
        
        # Load glitch texture
        self.glitch_texture = Material("images/20230714-_DSC8634.jpg")
        
        self.main_loop()

    def create_shader(self, vertex_file_path, fragment_file_path):
        with open(vertex_file_path, 'r') as f:
            vertex_src = ''.join(f.readlines())
            
        with open(fragment_file_path, 'r') as f:
            fragment_src = ''.join(f.readlines())
            
        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )
        
        return shader

    def main_loop(self):
        start_time = time.time()
        running = True

        while running:
            current_time = time.time() - start_time
            
            # Check events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Refresh screen
            glClear(GL_COLOR_BUFFER_BIT)
            
            # Use shader program and bind VAO for triangle
            glUseProgram(self.shader)
            self.glitch_texture.use()
            glBindVertexArray(self.triangle.vao)
            
            self.triangle.update(current_time)
            
            # Draw triangle using currently bound shader and VAO
            glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertex_count)
            
            pygame.display.flip()

            # Timing
            self.clock.tick(360)

        self.quit()

    def quit(self):
        self.triangle.delete()
        self.glitch_texture.delete()
        glDeleteProgram(self.shader)
        pygame.quit()

class Triangle:
    
    def __init__(self) -> None:
        self.vertex_count = 3
        
        # convert to type readable by graphics card
        # x, y, z, r, g, b, s, t
        self.vertices = np.array([
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0,
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0
        ], dtype = np.float32)
        
        # create VAO and VBO and binds them
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        
        # send the buffer vertex data to the VBO
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        # set up position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        
        # set up colour attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        
        # set up texture attribute
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))
        
    def update(self, time):
        vertex_stride = 8
        
        colour_speed = 4
        position_speed = 2
        radius = 0.1
        brightness = 1
        
        # Update vertex positions to move in a circle
        self.vertices[0 * vertex_stride + 0] = math.sin(position_speed * time + 1.0) * radius - 0.5
        self.vertices[0 * vertex_stride + 1] = math.cos(position_speed * time + 1.0) * radius - 0.5
        self.vertices[1 * vertex_stride + 0] = math.sin(position_speed * time + 2.0) * radius + 0.5
        self.vertices[1 * vertex_stride + 1] = math.cos(position_speed * time + 2.0) * radius - 0.5
        self.vertices[2 * vertex_stride + 0] = math.sin(position_speed * time + 3.0) * radius      
        self.vertices[2 * vertex_stride + 1] = math.cos(position_speed * time + 3.0) * radius + 0.5
        
        # Update colors to cycle through RGB smoothly
        self.vertices[0 * vertex_stride + 3 : 0 * vertex_stride + 6] = (
            brightness * (0.5 * math.sin(colour_speed * time + 0 * math.pi / 3)+ 0.5),
            brightness * (0.5 * math.sin(colour_speed * time + 2 * math.pi / 3)+ 0.5),
            brightness * (0.5 * math.sin(colour_speed * time + 4 * math.pi / 3)+ 0.5)
        )
        self.vertices[1 * vertex_stride + 3 : 1 * vertex_stride + 6] = (
            brightness * (0.5 * math.sin(colour_speed * time + 2 * math.pi / 3)+ 0.5),
            brightness * (0.5 * math.sin(colour_speed * time + 4 * math.pi / 3)+ 0.5),
            brightness * (0.5 * math.sin(colour_speed * time + 0 * math.pi / 3)+ 0.5)
        )
        self.vertices[2 * vertex_stride + 3 : 2 * vertex_stride + 6] = (
            brightness * (0.5 * math.sin(colour_speed * time + 4 * math.pi / 3)+ 0.5),
            brightness * (0.5 * math.sin(colour_speed * time + 0 * math.pi / 3)+ 0.5),
            brightness * (0.5 * math.sin(colour_speed * time + 2 * math.pi / 3)+ 0.5)
        )
        
        # Update the VBO with the new vertex data
        # glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_DYNAMIC_DRAW)
        
    def delete(self):
        # delete VAO and VBO
        glDeleteVertexArrays(1, (self.vao, ))
        glDeleteBuffers(1, (self.vbo, ))
        
class Material:
    
    def __init__(self, filepath) -> None:
        # Generate texture ID and bind as 2D texture
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        
        # Set texture wrapping to repeat for S and T axes
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        # Set texture filtering (scaling), nearest for minimizing, linear for magnifying
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Load image and convert for OpenGL
        image = pygame.image.load(filepath).convert()
        image_width, image_height = image.get_rect().size
        image_data = pygame.image.tostring(image, "RGBA")
        
        # Create new texture from image data, setting it as the current texture of the bound texture object
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
    def use(self):
        # Activate and bind the first texture unit
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        
    def delete(self):
        glDeleteTextures(1, (self.texture, ))

if __name__ == "__main__":
    myApp = App()