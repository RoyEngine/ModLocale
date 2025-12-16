package second_in_command.ui.tooltips

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.impl.codex.CodexDataV2
import com.fs.starfarer.api.ui.BaseTooltipCreator
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.misc.addPara
import second_in_command.misc.codex.CodexHandler
import second_in_command.specs.SCBaseAptitudePlugin
import second_in_command.specs.SCBaseSkillPlugin

class SCSkillTooltipCreator(var data: SCData, var skill: SCBaseSkillPlugin, var aptitude: SCBaseAptitudePlugin, var requiredSkillPoints: Int, var pickOnlyOne: Boolean) : BaseTooltipCreator() {


    var sectionMeetsRequirements = true

    override fun isTooltipExpandable(tooltipParam: Any?): Boolean {
        //return skill.spec.modname != "SecondInCommand"
        return false
    }

    override fun getTooltipWidth(tooltipParam: Any?): Float {
        return 700f
    }

    override fun createTooltip(tooltip: TooltipMakerAPI?, expanded: Boolean, tooltipParam: Any?) {

        var isOrigin = skill.getId() == aptitude.getOriginSkillId()

        tooltip!!.addTitle(skill.getName(), aptitude.getColor())

        /*if (!Global.getSettings().isShowingCodex) */tooltip.codexEntryId = CodexHandler.getAptitudEntryId(aptitude.id)

        var affectsString = skill.getAffectsString()

        tooltip.addSpacer(10f)
        tooltip.addPara("影响：{$affectsString", 0f, Misc.getGrayColor(), Misc.getBasePlayerColor(), affectsString)
        tooltip.addSpacer(10f)

        skill.addTooltip(data, tooltip)

        var elite = false
        if (elite) {
            tooltip.addSpacer(10f)
            tooltip.addPara("该技能为精英技能，比普通技能更强", 0f, Misc.getStoryOptionColor(),Misc.getStoryOptionColor())
        }
        if (!sectionMeetsRequirements || pickOnlyOne) {
            tooltip.addSpacer(10f)
        }

        if (!sectionMeetsRequirements) {
            var addedS = ""
            if (requiredSkillPoints >= 2) addedS = "s"
		tooltip.addPara("需要掌握 $requiredSkillPoints 种低阶技能}。", 0f, Misc.getNegativeHighlightColor(), Misc.getNegativeHighlightColor())
        }

        if (pickOnlyOne) {
            tooltip.addPara("该阶技能只能掌握其中一种", 0f, Misc.getNegativeHighlightColor(), Misc.getNegativeHighlightColor())
        }

        //RATs Whichmod feature is capable of showing this much better now.
        /*if (aptitude.spec.modSpec.id != "second_in_command") {
            tooltip.addSpacer(10f)
            //tooltip.addPara("Skill added by \"$modname\"", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
            tooltip.addPara("[${aptitude.spec.modSpec.name}]", 0f, Misc.getGrayColor(), Misc.getHighlightColor(), "$")
        }*/

        tooltip.addSpacer(2f)

    }



}