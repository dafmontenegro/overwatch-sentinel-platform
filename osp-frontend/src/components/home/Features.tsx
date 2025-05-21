import React from 'react';

const Features: React.FC = () => {
  const featuresList = [
    {
      id: 1,
      title: "Detección Inteligente",
      description: "Reconocimiento automático de objetos utilizando TensorFlow Lite en hardware de bajo consumo.",
      icon: "🔍"
    },
    {
      id: 2,
      title: "Grabación Optimizada",
      description: "Solo se activa la grabación cuando se detectan objetos en la zona segura, ahorrando espacio y recursos.",
      icon: "📹"
    },
    {
      id: 3,
      title: "Acceso Seguro",
      description: "Videos almacenados en servidor central con acceso HTTPS y autenticación de usuarios.",
      icon: "🔒"
    },
    {
      id: 4,
      title: "Interfaz Intuitiva",
      description: "Visualización en tiempo real y acceso a grabaciones históricas mediante calendario interactivo.",
      icon: "📅"
    }
  ];

  return (
    <section id="features" className="py-16 bg-white">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-asphalt mb-4">Características</h2>
          <div className="w-16 h-1 bg-capri mx-auto"></div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {featuresList.map(feature => (
            <div key={feature.id} className="bg-gray-50 p-6 rounded-lg shadow-sm hover:shadow-md transition duration-300">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-2 text-asphalt">{feature.title}</h3>
              <p className="text-asphalt">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;