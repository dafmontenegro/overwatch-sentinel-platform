import React from 'react';

const AboutUs: React.FC = () => {
  return (
    <section id="about" className="py-16 bg-gray-50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-asphalt mb-4">Sobre OSP</h2>
          <div className="w-16 h-1 bg-capri mx-auto"></div>
        </div>
        
        <div className="max-w-4xl mx-auto">
          <p className="text-lg text-asphalt mb-6">
            OSP (Overwatch Sentinel Platform) es una plataforma de software para la vigilancia automatizada 
            basada en visión por computadora, diseñada para funcionar sobre hardware de bajo consumo.
          </p>
          
          <p className="text-lg text-asphalt mb-6">
            Este proyecto construye un sistema de detección de objetos en tiempo real utilizando una Raspberry Pi y una cámara. 
            Captura vídeo en directo, lo procesa con un modelo TensorFlow Lite para detectar objetos específicos y guarda los eventos importantes como archivos de vídeo. 
            Para gestionar estas tareas de forma eficiente, utiliza computación paralela con subprocesos. El sistema proporciona alertas visuales mediante LED y sonoras a través de un zumbador, 
            mostrando su capacidad para controlar acciones del mundo real, que también puede ampliarse para gestionar circuitos o enviar señales. 
            Para la supervisión en tiempo real se crea un servidor de red local que permite a los usuarios ver vídeo en directo, acceder a grabaciones guardadas y revisar registros sin problemas.
          </p>
          
          <p className="text-lg text-asphalt">
            Cuando un objeto de interés entra en la zona segura, el sistema activa automáticamente la grabación de video. 
            De este modo, se optimiza el uso de recursos, ya que solo se almacena material cuando se detecta actividad relevante.
          </p>
        </div>
      </div>
    </section>
  );
};

export default AboutUs;
