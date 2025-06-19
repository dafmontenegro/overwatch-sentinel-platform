import React, { useState } from 'react';

const ContactSection: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulación de envío de formulario
    try {
      // Aquí iría la lógica real de envío al backend
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setSubmitMessage({
        type: 'success',
        text: '¡Mensaje enviado correctamente! Nos pondremos en contacto pronto.'
      });
      
      // Resetear formulario
      setFormData({
        name: '',
        email: '',
        message: ''
      });
    } catch (error) {
      setSubmitMessage({
        type: 'error',
        text: 'Hubo un error al enviar el mensaje. Por favor, inténtelo de nuevo.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <section id="contact" className="py-16 bg-gray-50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-asphalt mb-4">Contacto</h2>
          <div className="w-16 h-1 bg-capri mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">¿Tiene preguntas sobre OSP? Contáctenos</p>
        </div>
        
        <div className="max-w-2xl mx-auto">
          {submitMessage && (
            <div className={`mb-6 p-4 rounded ${submitMessage.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {submitMessage.text}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="name" className="block text-asphalt font-medium mb-2">Nombre</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-capri"
                required
              />
            </div>
            
            <div className="mb-4">
              <label htmlFor="email" className="block text-asphalt font-medium mb-2">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-capri"
                required
              />
            </div>
            
            <div className="mb-6">
              <label htmlFor="message" className="block text-asphalt font-medium mb-2">Mensaje</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                rows={5}
                className="w-full px-4 py-2 border border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-capri"
                required
              ></textarea>
            </div>
            
            <div className="text-center">
              <button
                type="submit"
                disabled={isSubmitting}
                className="bg-asphalt text-white font-medium py-3 px-8 rounded-lg shadow-md hover:bg-capri transition duration-300 disabled:opacity-70"
              >
                {isSubmitting ? 'Enviando...' : 'Enviar Mensaje'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;