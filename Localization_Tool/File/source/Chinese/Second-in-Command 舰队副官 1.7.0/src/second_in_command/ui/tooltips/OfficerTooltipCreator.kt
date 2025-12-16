package second_in_command.ui.tooltips

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.ui.BaseTooltipCreator
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCUtils
import second_in_command.specs.SCOfficer
import second_in_command.ui.SCSkillMenuPanel
import second_in_command.ui.elements.OfficerXPBar

class OfficerTooltipCreator(var officer: SCOfficer?, var isAtColony: Boolean, var openedFromPicker: Boolean) : BaseTooltipCreator() {




    override fun getTooltipWidth(tooltipParam: Any?): Float {
        return 400f
    }

    override fun createTooltip(tooltip: TooltipMakerAPI?, expanded: Boolean, tooltipParam: Any?) {

        if (officer == null) {

            tooltip!!.addPara("此栏位可用于指派{执行军官}。执行军官将基于他们的天赋具备一系列技能。{只有被指派的执行军官的技能会生效}。 ",
                0f, Misc.getTextColor(), Misc.getHighlightColor(), "执行军官", "只有被指派的执行军官的技能会生效")

            tooltip.addSpacer(10f)

            tooltip!!.addPara("你偶尔能在殖民地的{通讯目录}中找到待雇佣的执行军官。 他们也可能在探险时出现在被遗弃舰船上的{休眠舱}之中。",
                0f, Misc.getTextColor(), Misc.getHighlightColor(), "通讯目录", "休眠舱")

            tooltip.addSpacer(10f)

            addCRWarning(tooltip)

            tooltip.addSpacer(10f)

		tooltip!!.addPara("左键单击}选择要指派的执行军官。{右键单击}撤销其指派。",
                    0f, Misc.getTextColor(), Misc.getHighlightColor(), "左键单击", "右键单击")





            return
        }

        var plugin = officer!!.getAptitudePlugin()
        var width = getTooltipWidth(null)

        var title = tooltip!!.addTitle(officer!!.person.nameString, plugin.getColor())
        var xPos = width / 2 - title.computeTextWidth(title.text) / 2
        title.position.inTL(xPos, 5f)

        var required = officer!!.getRequiredXP()
        if (officer!!.getCurrentLevel() == officer!!.getMaxLevel()) required = 0f
        var bar = OfficerXPBar(officer!!.getExperiencePoints(), required, plugin.getColor(), tooltip!!, 180f, 25f).apply {
            position.inTMid(25f)
        }


        bar.addText("等级 ${officer!!.getCurrentLevel().toInt()}", Misc.getTextColor())
        bar.centerText()

        var experience = officer!!.getExperiencePoints().toInt()
        var experienceNeeded = officer!!.getRequiredXP().toInt() - experience

        var experienceString = Misc.getWithDGS(experience.toFloat())
        var experienceNeededString = Misc.getWithDGS(experienceNeeded.toFloat())

        var inactiveGain = (SCOfficer.inactiveXPMult * 100).toInt()

var firstPara = tooltip.addPara("${officer!!.person.nameString} 具备 ${plugin.getName()} 天赋。该天赋等级上限为 ${officer!!.getMaxLevel()}}。", 0f,
        Misc.getTextColor(), Misc.getHighlightColor(), "")
        firstPara.position.inTL(5f, 60f)

        tooltip.addSpacer(10f)

        firstPara.setHighlight(officer!!.person.nameString, plugin.getName(), "${officer!!.getMaxLevel()}")
        firstPara.setHighlightColors(Misc.getHighlightColor(), plugin.getColor(), Misc.getHighlightColor())

        var isAtMax = officer!!.getMaxLevel() == officer!!.getCurrentLevel()

        if (isAtMax) {
            tooltip.addPara("${officer!!.person.heOrShe.capitalize()} 已经达到了${officer!!.person.hisOrHer}的等级上限。", 0f)
        } else {
            tooltip.addPara("${officer!!.person.heOrShe.capitalize()}当前等级 ${officer!!.getCurrentLevel()}}。 " +
                    "${officer!!.person.heOrShe.capitalize()}现有 $experienceString 经验值，升级还需要获得 $experienceNeededString 经验值。", 0f,
                Misc.getTextColor(), Misc.getHighlightColor(), "${officer!!.getCurrentLevel()}", "$experienceString", "$experienceNeededString")
        }



        tooltip.addSpacer(10f)

        tooltip.addPara("所有军官都只会{从战斗中获得经验}。军官若未被指派，便只能以 $inactiveGain%% 的效率获得经验。", 0f, Misc.getTextColor(), Misc.getHighlightColor(),
            "从战斗中获得经验" ,"$inactiveGain%")


        if (!SCUtils.isAssociatesBackgroundActive())  {
            tooltip.addSpacer(10f)
            addCRWarning(tooltip)
        }

        /* if (officer!!.getAptitudePlugin().getRequiresDock()) {
             tooltip.addSpacer(10f)
             tooltip.addPara("This officer can only be assigned and un-assigned while the fleet is docked to a colony due to the preparations required for ${officer!!.person.hisOrHer} field of work.", 0f, Misc.getNegativeHighlightColor(), Misc.getNegativeHighlightColor())
         }*/


        if (!openedFromPicker) {

            tooltip.addSpacer(10f)
            var extra = ""
            if (Global.getSector().playerPerson.stats.storyPoints <= 3) {
                extra = "你现在没有足够的故事点。"
            }

		var label = tooltip!!.addPara("用鼠标指向该军官的头像再按下 \"R\" 键，便可以重置其技能。这需要花费 4 故事点}。尚未结束技能修改前无法重置技能。{$extra", 0f,
                Misc.getTextColor(), Misc.getHighlightColor(), "")

            label.setHighlight("R", "4 故事点", extra)
            label.setHighlightColors(Misc.getHighlightColor(), Misc.getStoryOptionColor(), Misc.getNegativeHighlightColor())

            tooltip.addSpacer(10f)


            if (!SCUtils.isAssociatesBackgroundActive()) {
			tooltip!!.addPara("左键单击}选择要指派的执行军官。{右键单击}撤销其指派。",
                    0f, Misc.getTextColor(), Misc.getHighlightColor(), "左键单击", "右键单击")
            } else {
                tooltip!!.addPara("由于你选择的出身背景，{这名军官无法被移除或替换}。另一方面，点击其头像将允许你更改他们的{姓名}和{头像}。",
                    0f, Misc.getTextColor(), Misc.getHighlightColor(), "这名军官无法被移除或替换","姓名", "头像")
            }


        }

        tooltip.addSpacer(30f)

    }

    fun addCRWarning(tooltip: TooltipMakerAPI) {

        var colonyText = "你现在位于一处殖民地附近"
        var colonyColor = Misc.getPositiveHighlightColor()
        var penalty = (SCSkillMenuPanel.crCost * 100f).toInt()

        if (!isAtColony) {
            colonyText = "你现在远离任何一处殖民地"
            colonyColor = Misc.getNegativeHighlightColor()
        }

	var colonyLabel = tooltip.addPara("当舰队并未靠近或停靠{非敌对殖民地}时，替换或撤销指派一名执行军官会使整支舰队的{战备值}降低 $penalty%%}。{$colonyText}。",
            0f, Misc.getTextColor(), Misc.getHighlightColor())

        colonyLabel.setHighlight("非敌对殖民地", "战备值", "$penalty%", colonyText)
        colonyLabel.setHighlightColors(Misc.getHighlightColor(), Misc.getNegativeHighlightColor(), Misc.getHighlightColor(), colonyColor)
    }


}