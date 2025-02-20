"""
Template service for managing and rendering templates.
"""
import re
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from jinja2 import Environment, BaseLoader, TemplateError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.api.models.template import (
    Template,
    TemplateInstance,
    TemplateCreate,
    TemplateUpdate
)

logger = logging.getLogger(__name__)

class TemplateService:
    """Service for handling templates."""

    def __init__(self, db: Session):
        self.db = db
        self.jinja_env = Environment(
            loader=BaseLoader(),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def create_template(self, template: TemplateCreate, user_id: int) -> Template:
        """Create a new template."""
        # Validate template variables
        self._validate_template(template.content, template.variables)

        # Create template
        db_template = Template(
            name=template.name,
            description=template.description,
            type=template.type,
            content=template.content,
            variables=template.variables,
            created_by=user_id
        )

        try:
            self.db.add(db_template)
            
            # If this is a default template, unset other defaults
            if template.is_default:
                self._unset_other_defaults(template.type)
                db_template.is_default = True
            
            self.db.commit()
            self.db.refresh(db_template)
            return db_template
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error creating template")

    def update_template(
        self,
        template_id: int,
        update_data: TemplateUpdate,
        user_id: int
    ) -> Optional[Template]:
        """Update a template."""
        template = self.get_template(template_id)
        if not template:
            return None

        # Validate new content if provided
        if update_data.content is not None:
            variables = update_data.variables or template.variables
            self._validate_template(update_data.content, variables)

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(template, field, value)

        # Increment version if content changed
        if 'content' in update_dict:
            template.version += 1

        # Handle default flag
        if update_data.is_default:
            self._unset_other_defaults(template.type)

        template.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(template)
            return template
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error updating template")

    def delete_template(self, template_id: int) -> bool:
        """Delete a template."""
        template = self.get_template(template_id)
        if not template:
            return False

        try:
            self.db.delete(template)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Cannot delete template with existing instances")

    def get_template(self, template_id: int) -> Optional[Template]:
        """Get a template by ID."""
        return self.db.query(Template).filter(Template.id == template_id).first()

    def get_templates(
        self,
        type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Template]:
        """Get all templates."""
        query = self.db.query(Template)
        
        if type:
            query = query.filter(Template.type == type)
        if active_only:
            query = query.filter(Template.is_active == True)
            
        return query.order_by(Template.name).all()

    def get_default_template(self, type: str) -> Optional[Template]:
        """Get default template for a type."""
        return self.db.query(Template).filter(
            Template.type == type,
            Template.is_default == True,
            Template.is_active == True
        ).first()

    def create_instance(
        self,
        template_id: int,
        variables: Dict[str, Any],
        user_id: int
    ) -> TemplateInstance:
        """Create a template instance."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")

        # Render template
        content = self.render_template(template, variables)

        # Create instance
        instance = TemplateInstance(
            template_id=template_id,
            content=content,
            variables_used=variables,
            created_by=user_id
        )

        try:
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error creating template instance")

    def render_template(
        self,
        template: Template,
        variables: Dict[str, Any]
    ) -> str:
        """Render a template with variables."""
        try:
            # Validate variables
            self._validate_variables(template.variables, variables)
            
            # Create Jinja template
            jinja_template = self.jinja_env.from_string(template.content)
            
            # Render template
            return jinja_template.render(**variables)
        except TemplateError as e:
            logger.error(f"Error rendering template: {str(e)}")
            raise ValueError(f"Error rendering template: {str(e)}")

    def _validate_template(self, content: str, variables: Dict[str, Any]):
        """Validate template content and variables."""
        try:
            # Check template syntax
            self.jinja_env.from_string(content)
            
            # Extract variables from template
            var_pattern = r"{{\s*(\w+)\s*}}"
            template_vars = set(re.findall(var_pattern, content))
            
            # Validate all template variables are defined
            for var in template_vars:
                if var not in variables:
                    raise ValueError(f"Template variable '{var}' not defined")
                    
            # Validate variables schema
            for var, schema in variables.items():
                if not isinstance(schema, dict) or 'type' not in schema:
                    raise ValueError(f"Invalid schema for variable '{var}'")
        except Exception as e:
            raise ValueError(f"Template validation failed: {str(e)}")

    def _validate_variables(
        self,
        schema: Dict[str, Any],
        variables: Dict[str, Any]
    ):
        """Validate variables against schema."""
        for var, var_schema in schema.items():
            if var not in variables:
                raise ValueError(f"Required variable '{var}' missing")
                
            value = variables[var]
            var_type = var_schema['type']
            
            if var_type == 'string' and not isinstance(value, str):
                raise ValueError(f"Variable '{var}' must be a string")
            elif var_type == 'number' and not isinstance(value, (int, float)):
                raise ValueError(f"Variable '{var}' must be a number")
            elif var_type == 'boolean' and not isinstance(value, bool):
                raise ValueError(f"Variable '{var}' must be a boolean")
            elif var_type == 'date':
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except:
                    raise ValueError(f"Variable '{var}' must be a valid date (YYYY-MM-DD)")

    def _unset_other_defaults(self, type: str):
        """Unset default flag for other templates of same type."""
        self.db.query(Template).filter(
            Template.type == type,
            Template.is_default == True
        ).update({"is_default": False})